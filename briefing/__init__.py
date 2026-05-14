"""Public trending news aggregator — daily briefing generator."""

from __future__ import annotations

import json
import os
import time
import traceback
from datetime import datetime, timezone

from .config import CATEGORIES, DEEPSEEK_API_KEY, OUTPUT_DIR
from .curator import generate_overall, process_category, process_misc
from .fetchers import fetch_all_stories
from .renderer import render_fragment, render_standalone

__all__ = ["main"]


def write_outputs(fragment: str, standalone: str, meta: dict) -> None:
    out_dir = os.path.abspath(OUTPUT_DIR)
    os.makedirs(out_dir, exist_ok=True)

    index_path = os.path.join(out_dir, "index.html")
    fragment_path = os.path.join(out_dir, "briefing-fragment.html")
    meta_path = os.path.join(out_dir, "briefing-meta.json")

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(standalone)
    with open(fragment_path, "w", encoding="utf-8") as f:
        f.write(fragment)
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    print(f"Wrote standalone: {index_path}")
    print(f"Wrote fragment:   {fragment_path}")
    print(f"Wrote meta:       {meta_path}")


def main() -> None:
    print("=" * 65)
    print(" PUBLIC TRENDING NEWS AGGREGATOR — DAILY BRIEFING")
    print(f" {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f" DeepSeek: {'ENABLED' if DEEPSEEK_API_KEY else 'DISABLED (will write empty briefing)'}")
    print("=" * 65)

    try:
        all_stories = fetch_all_stories()
    except Exception as e:
        print(f"FATAL fetch error: {e}")
        traceback.print_exc()
        all_stories = {c: [] for c in CATEGORIES}

    total = sum(len(s) for s in all_stories.values())
    print(f"\nRaw stories: {total}")
    for cat, sl in all_stories.items():
        print(f"  {cat}: {len(sl)}")

    used: list[str] = []
    ai_results: dict[str, list[dict]] = {}
    for category in CATEGORIES:
        stories = all_stories.get(category, [])
        if not stories:
            ai_results[category] = []
            continue
        print(f"  Processing {category} ({len(stories)} raw)...")
        if category == "Miscellaneous":
            picks, used = process_misc(stories, used)
        else:
            picks, used = process_category(category, stories, used)
        ai_results[category] = picks
        time.sleep(1)

    top_candidates: list[tuple[str, dict]] = []
    for category in CATEGORIES:
        for s in ai_results.get(category, [])[:1]:
            top_candidates.append((category, s))
    top_candidates.sort(key=lambda x: len(x[1].get("brief", "")), reverse=True)
    overall = generate_overall(top_candidates[:3])

    now_utc = datetime.now(timezone.utc)
    today_human = now_utc.strftime("%B %d, %Y")
    fragment = render_fragment(ai_results, overall, today_human)
    standalone = render_standalone(fragment, today_human)

    story_count = sum(len(picks) for picks in ai_results.values())
    meta = {
        "updated_iso": now_utc.isoformat().replace("+00:00", "Z"),
        "updated_human": today_human,
        "weekday": now_utc.strftime("%A"),
        "story_count": story_count,
        "category_count": len(CATEGORIES),
    }

    write_outputs(fragment, standalone, meta)
    print(f"\nFinished — {story_count} briefs across {len(CATEGORIES)} categories.")
