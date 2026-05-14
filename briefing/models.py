"""Data model and engagement / recency weighting helpers."""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import requests

from .config import (
    MISC_REDDIT_SUBS,
    MISC_RSS_FEEDS,
    RECENCY_WINDOW_HOURS,
    REQUEST_TIMEOUT,
    SCORE_NORMALIZATION_CAP,
    TRENDING_BIAS,
    USER_AGENT,
)


@dataclass
class RawStory:
    title: str
    url: str
    source: str
    category: str
    score: int = 0
    comment_count: int = 0
    published: Optional[datetime] = None
    hours_old: float = 999.0
    theme: str = ""


def fetch_json(url: str, headers: Optional[dict] = None) -> Optional[dict]:
    h = {"User-Agent": USER_AGENT}
    if headers:
        h.update(headers)
    try:
        resp = requests.get(url, headers=h, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None


def parse_timestamp(ts: float) -> Optional[datetime]:
    try:
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    except (TypeError, ValueError, OSError):
        return None


def parse_rss_date(entry) -> Optional[datetime]:
    try:
        if getattr(entry, "published_parsed", None):
            return datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
        if getattr(entry, "updated_parsed", None):
            return datetime.fromtimestamp(time.mktime(entry.updated_parsed), tz=timezone.utc)
    except Exception:
        pass
    return None


def hours_ago(dt: Optional[datetime]) -> float:
    if not dt:
        return 999.0
    delta = datetime.now(timezone.utc) - dt
    return max(0, delta.total_seconds() / 3600)


def compute_weight(story: RawStory) -> float:
    # Engagement carries the larger weight so a sustained multi-day story
    # beats a fresh blip with the same raw score; recency still nudges toward
    # stories from the last few days within the 7-day window.
    score_factor = min(max(story.score, 0), SCORE_NORMALIZATION_CAP) / SCORE_NORMALIZATION_CAP
    engagement_boost = min(story.comment_count, 2000) / 2000 * 0.3
    score_factor = min(1.0, score_factor + engagement_boost)
    recency_factor = max(0.0, 1.0 - story.hours_old / RECENCY_WINDOW_HOURS)
    return TRENDING_BIAS * score_factor + (1.0 - TRENDING_BIAS) * recency_factor


def clean_source(raw: str) -> str:
    clean = raw.replace("feeds.", "").replace("www.", "").replace("rss.", "")
    return clean.split("/")[0] if "/" in clean else clean


def theme_for_reddit_sub(sub: str) -> str:
    for theme, subs in MISC_REDDIT_SUBS.items():
        if sub in subs:
            return theme
    return "Other"


def theme_for_rss_feed(feed_url: str) -> str:
    for theme, feeds in MISC_RSS_FEEDS.items():
        if feed_url in feeds:
            return theme
    return "Other"
