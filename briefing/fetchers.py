"""Fetchers for Reddit, Hacker News, RSS, Google News, and holidays."""

from __future__ import annotations

import time
from datetime import datetime, timezone

import feedparser

from .config import (
    CATEGORIES,
    GOOGLE_NEWS_TOPICS,
    REDDIT_SUBS,
    RSS_FEEDS,
    RSS_HARD_CUTOFF_HOURS,
    USER_AGENT,
)
from .models import (
    RawStory,
    clean_source,
    fetch_json,
    hours_ago,
    parse_rss_date,
    parse_timestamp,
    theme_for_reddit_sub,
    theme_for_rss_feed,
)


def fetch_reddit(subreddit: str) -> list[RawStory]:
    url = f"https://www.reddit.com/r/{subreddit}/top.json?t=week&limit=15"
    data = fetch_json(url)
    stories: list[RawStory] = []
    if not data or "data" not in data:
        return stories
    for child in data["data"].get("children", []):
        post = child.get("data", {})
        pub = parse_timestamp(post.get("created_utc", 0))
        if hours_ago(pub) > 7 * 24:
            continue
        title = (post.get("title") or "").strip()
        permalink = post.get("permalink", "")
        url_link = post.get("url", "")
        score = post.get("score", 0)
        comments = post.get("num_comments", 0)
        link = url_link if url_link and not url_link.startswith("/r/") else f"https://www.reddit.com{permalink}"
        if score < 50:
            continue
        stories.append(RawStory(
            title=title, url=link, source=f"reddit.com/r/{subreddit}",
            category="", score=score, comment_count=comments,
            published=pub, hours_old=hours_ago(pub),
        ))
    return stories


def fetch_hackernews() -> list[RawStory]:
    stories: list[RawStory] = []
    best_ids = fetch_json("https://hacker-news.firebaseio.com/v0/beststories.json")
    if not best_ids:
        return stories
    for story_id in best_ids[:25]:
        item = fetch_json(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json")
        if not item:
            continue
        pub = parse_timestamp(item.get("time", 0))
        if hours_ago(pub) > 7 * 24:
            continue
        title = (item.get("title") or "").strip()
        url = item.get("url") or f"https://news.ycombinator.com/item?id={story_id}"
        score = item.get("score", 0)
        comments = item.get("descendants", 0)
        if score < 30:
            continue
        stories.append(RawStory(
            title=title, url=url, source="news.ycombinator.com",
            category="Tech", score=score, comment_count=comments,
            published=pub, hours_old=hours_ago(pub),
        ))
    return stories


def fetch_rss(feed_url: str, category: str) -> list[RawStory]:
    stories: list[RawStory] = []
    try:
        parsed = feedparser.parse(feed_url, agent=USER_AGENT)
        source = clean_source(feed_url.split("/")[2] if "//" in feed_url else feed_url)
        for rank, entry in enumerate(parsed.entries[:12]):
            title = (entry.get("title") or "").strip()
            link = entry.get("link", "")
            pub = parse_rss_date(entry)
            if not title or len(title) < 10:
                continue
            hours = hours_ago(pub)
            if pub and hours > RSS_HARD_CUTOFF_HOURS:
                continue
            stories.append(RawStory(
                title=title, url=link, source=source,
                category=category, score=max(50, 400 - rank * 30),
                published=pub, hours_old=hours,
            ))
    except Exception:
        pass
    return stories


def fetch_google_news(category: str) -> list[RawStory]:
    topic_id = GOOGLE_NEWS_TOPICS.get(category)
    if not topic_id:
        return []
    url = f"https://news.google.com/rss/topics/{topic_id}?hl=en-US&gl=US&ceid=US:en"
    return fetch_rss(url, category)


def fetch_holidays() -> list[RawStory]:
    stories: list[RawStory] = []
    now = datetime.now(timezone.utc)
    today_str = now.strftime("%Y-%m-%d")

    for country in ["US", "GB", "CA"]:
        try:
            data = fetch_json(f"https://date.nager.at/api/v3/PublicHolidays/{now.year}/{country}")
            if not data:
                continue
            for entry in data:
                if entry.get("date") == today_str:
                    name = entry.get("name") or entry.get("localName") or ""
                    if not name:
                        continue
                    stories.append(RawStory(
                        title=f"Today is {name} in {country}",
                        url=f"https://date.nager.at/PublicHoliday/Country/{country}",
                        source="date.nager.at",
                        category="Miscellaneous", score=300,
                        published=now, hours_old=0.0, theme="Holidays",
                    ))
        except Exception:
            pass

    try:
        feed_stories = fetch_rss("https://www.checkiday.com/rss.php", "Miscellaneous")
        for s in feed_stories[:5]:
            s.theme = "Holidays"
            stories.append(s)
    except Exception:
        pass

    return stories


def fetch_all_stories() -> dict[str, list[RawStory]]:
    all_stories: dict[str, list[RawStory]] = {c: [] for c in CATEGORIES}

    print("Fetching Reddit...")
    for category, subs in REDDIT_SUBS.items():
        for sub in subs:
            time.sleep(0.5)
            try:
                for s in fetch_reddit(sub):
                    s.category = category
                    if category == "Miscellaneous":
                        s.theme = theme_for_reddit_sub(sub)
                    all_stories[category].append(s)
            except Exception:
                pass

    print("Fetching Hacker News...")
    try:
        for s in fetch_hackernews():
            all_stories["Tech"].append(s)
    except Exception:
        pass

    print("Fetching RSS feeds...")
    for category, feeds in RSS_FEEDS.items():
        for feed_url in feeds:
            time.sleep(0.4)
            try:
                feed_stories = fetch_rss(feed_url, category)
                if category == "Miscellaneous":
                    theme = theme_for_rss_feed(feed_url)
                    for s in feed_stories:
                        s.theme = theme
                all_stories[category].extend(feed_stories)
            except Exception:
                pass

    print("Fetching holidays...")
    try:
        all_stories["Miscellaneous"].extend(fetch_holidays())
    except Exception:
        pass

    print("Fetching Google News...")
    for category in CATEGORIES:
        time.sleep(0.4)
        try:
            all_stories[category].extend(fetch_google_news(category))
        except Exception:
            pass

    return all_stories
