"""LLM curation: take raw weighted stories, produce the final briefing."""

from __future__ import annotations

import time

import requests

from .config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_API_URL,
    DEEPSEEK_MODEL,
    MISC_THEME_LIMIT,
    MISC_THEMES,
)
from .models import RawStory, compute_weight


def call_deepseek(system_prompt: str, user_prompt: str) -> str:
    if not DEEPSEEK_API_KEY:
        return ""
    try:
        resp = requests.post(
            DEEPSEEK_API_URL,
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": DEEPSEEK_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "temperature": 0.3,
                "max_tokens": 4000,
            },
            timeout=120,
        )
        if resp.status_code != 200:
            print(f"DeepSeek HTTP {resp.status_code}")
            return ""
        return resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception as e:
        print(f"DeepSeek error: {e}")
        return ""


def _stories_to_text(stories: list[RawStory]) -> str:
    lines = []
    for i, s in enumerate(stories, 1):
        age = f"{int(s.hours_old)}h ago" if s.hours_old < 48 else f"{int(s.hours_old/24)}d ago"
        engagement = f"score={s.score} comments={s.comment_count}" if s.score > 0 else "RSS"
        lines.append(f"[{i}] TITLE: {s.title}\n    SOURCE: {s.source} | {engagement} | {age}\n    URL: {s.url}")
    return "\n".join(lines)


def _parse_picks(content: str) -> list[dict]:
    results: list[dict] = []
    current: dict = {}
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("STORY"):
            if current.get("headline"):
                results.append(current)
            current = {}
        elif line.startswith("HEADLINE:"):
            current["headline"] = line.split(":", 1)[1].strip()
        elif line.startswith("BRIEF:"):
            current["brief"] = line.split(":", 1)[1].strip()
        elif line.startswith("SOURCE:"):
            current["source"] = line.split(":", 1)[1].strip()
        elif line.startswith("URL:"):
            current["url"] = line.split(":", 1)[1].strip()
        elif line and "brief" in current and not line.startswith(("STORY", "HEADLINE", "SOURCE", "URL")):
            current["brief"] += " " + line
    if current.get("headline"):
        results.append(current)
    return results


def process_category(category: str, stories: list[RawStory], used: list[str]) -> tuple[list[dict], list[str]]:
    if not stories or not DEEPSEEK_API_KEY:
        return [], used

    stories = sorted(stories, key=compute_weight, reverse=True)[:30]

    blocked = "\n".join(f"- {h}" for h in used) if used else "(none yet)"
    extra = ""
    if category == "Social Media":
        extra = (
            "CRITICAL: Select stories about what is actually trending ON social media platforms this week — "
            "viral videos, meme culture, creator drama, TikTok trending sounds/challenges, X/Twitter discourse, "
            "YouTube creator moments, Instagram viral posts, Reddit-going-viral stories. "
            "Prioritize what real people are sharing, watching, and talking about online right now. "
            "Draw on sources like TikTok charts, YouTube trending, Twitter/X trending, "
            "Reddit r/popular, Billboard social charts, and trending Google searches. "
            "NOT platform business deals, earnings reports, or ad-tech acquisitions.\n\n"
        )
    elif category == "Pop Culture":
        extra = (
            "CRITICAL: At least ONE of the 3 stories MUST cover what is trending or newly released on a "
            "streaming platform — specifically one of: Netflix, Hulu, Paramount+, Max, Disney+, Apple TV+, "
            "or Peacock. This should be a show, film, or docuseries that people are actively watching and "
            "talking about this week. The other 2 stories can cover music charts, movies, celebrity culture, "
            "award shows, or other pop culture topics.\n\n"
        )

    system_prompt = (
        "You are a senior editor curating the most remarkable, conversation-worthy stories "
        "of the past 7 days for a daily briefing. Strongly prefer stories that have sustained "
        "audience attention and discussion throughout the week — the ones people are still talking "
        "about today, not minor items that simply broke in the last hour. "
        "Every word earns its place. No filler. Two sentences per brief."
    )
    user_prompt = (
        f"CATEGORY: {category}\n\n{extra}"
        f"ALREADY USED (do NOT repeat):\n{blocked}\n\n"
        f"Candidate stories (pre-sorted by 7-day trending strength — top entries have the most sustained engagement):\n"
        f"{_stories_to_text(stories)}\n\n"
        f"Pick the top 3 most remarkable / widely-discussed stories from the PAST 7 DAYS. "
        f"Strongly favor stories that have maintained audience attention and discussion over the full week "
        f"versus stories that simply broke in the last few hours. "
        f"Output each as:\n"
        f"STORY 1\nHEADLINE: [max 15 words]\nBRIEF: [2 sentences: what happened, why it matters]\n"
        f"SOURCE: [domain only]\nURL: [story URL]\n\n"
        f"STORY 2\n...\nSTORY 3\n...\n\n"
        f"Rules: never repeat already-used stories. No filler. End every sentence with a period."
    )

    content = call_deepseek(system_prompt, user_prompt)
    if not content:
        return [], used
    picks = _parse_picks(content)[:3]
    for p in picks:
        used.append(p.get("headline", ""))
    return picks, used


def process_misc(stories: list[RawStory], used: list[str]) -> tuple[list[dict], list[str]]:
    if not stories or not DEEPSEEK_API_KEY:
        return [], used

    by_theme: dict[str, list[RawStory]] = {t: [] for t in MISC_THEMES}
    for s in stories:
        bucket = s.theme if s.theme in by_theme else "Other"
        by_theme[bucket].append(s)

    # Rank themes by the strength of their best candidate so the Misc section
    # only surfaces the top MISC_THEME_LIMIT themes for the day.
    theme_strength: list[tuple[str, float]] = []
    for theme in MISC_THEMES:
        bucket = sorted(by_theme.get(theme, []), key=compute_weight, reverse=True)
        by_theme[theme] = bucket
        if bucket:
            theme_strength.append((theme, compute_weight(bucket[0])))

    theme_strength.sort(key=lambda x: x[1], reverse=True)
    selected_themes = [t for t, _ in theme_strength[:MISC_THEME_LIMIT]]

    results: list[dict] = []
    for theme in selected_themes:
        theme_stories = by_theme.get(theme, [])
        if not theme_stories:
            continue
        hint = {
            "Weather": "notable weather events, severe weather, climate moments",
            "Music": "new releases, viral songs, concerts, artist milestones",
            "Archaeology": "newly discovered artifacts, dig sites, ancient civilizations",
            "Holidays": "today's holidays, observances, national days",
            "Religion": "faith news, theological stories, religion in culture",
            "Other": "a genuinely unusual or fascinating wildcard story",
        }.get(theme, "")
        blocked = "\n".join(f"- {h}" for h in used) if used else "(none yet)"

        system_prompt = (
            "You are a senior editor writing one short brief for a daily news briefing. "
            "Pick the most remarkable, conversation-worthy story of the past 7 days for this theme — "
            "not just whatever is freshest. Two sentences. Specific. No filler."
        )
        user_prompt = (
            f"MISC THEME: {theme}\nSurface: {hint}.\n\n"
            f"ALREADY USED:\n{blocked}\n\n"
            f"Candidates (pre-sorted by weekly trending strength):\n{_stories_to_text(theme_stories[:25])}\n\n"
            f"Pick exactly ONE — the most remarkable / widely-discussed of the past 7 days. "
            f"Output:\nSTORY 1\nHEADLINE: ...\nBRIEF: ...\nSOURCE: ...\nURL: ..."
        )
        content = call_deepseek(system_prompt, user_prompt)
        if not content:
            continue
        picks = _parse_picks(content)
        if picks:
            pick = picks[0]
            pick["theme"] = theme
            results.append(pick)
            used.append(pick.get("headline", ""))
        time.sleep(0.4)

    return results, used


def generate_overall(top_stories: list[tuple[str, dict]]) -> str:
    if not DEEPSEEK_API_KEY or not top_stories:
        return ""
    stories_text = "\n\n".join(
        f"[{cat}] {s.get('headline', '')}: {s.get('brief', '')}"
        for cat, s in top_stories
    )
    system = "You are an editor writing a daily briefing summary. Two sentences. Be specific."
    user = (
        f"Top stories:\n\n{stories_text}\n\n"
        f"Write EXACTLY two sentences summarizing today. Name the actual stories."
    )
    return call_deepseek(system, user)
