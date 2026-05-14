"""HTML rendering: standalone page + embeddable body fragment."""

from __future__ import annotations

import html

from .config import CATEGORIES, CATEGORY_ICON, THEME_ICON


EMBED_STYLES = """
<style>
.briefing-report * { box-sizing: border-box; }
.briefing-report { font-family: 'DM Sans', system-ui, sans-serif; max-width: 1200px; margin: 0 auto;
  background: #fff; border-radius: 14px; overflow: hidden;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08); color: #2c2520; }
.briefing-header { background: linear-gradient(135deg, #2d5040 0%, #3a6e54 50%, #4f8a6a 100%);
  padding: 22px 28px; color: #fff; }
.briefing-header h2 { margin: 0; font-family: 'Playfair Display', serif; font-size: 22px;
  font-weight: 600; letter-spacing: -0.3px; }
.briefing-header .briefing-sub { margin-top: 6px; font-size: 12px; opacity: 0.92;
  letter-spacing: 0.2px; }
.briefing-header .briefing-badge { display: inline-block; background: rgba(255,255,255,0.22);
  padding: 3px 10px; border-radius: 4px; font-size: 11px; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.5px; margin-right: 6px; }
.briefing-toc { padding: 16px 28px 6px; border-bottom: 1px solid #f1ebde;
  display: flex; flex-wrap: wrap; gap: 6px; background: #fdfbf8; }
.briefing-toc a { font-size: 12px; color: #2d5040; padding: 4px 10px; border-radius: 14px;
  text-decoration: none; background: #fff; border: 1px solid #e4dbcf; }
.briefing-toc a:hover { background: #f6efe3; }
.briefing-overall { padding: 18px 28px; background: #fdfbf8; border-bottom: 1px solid #f1ebde;
  font-family: 'EB Garamond', serif; font-size: 1.05rem; line-height: 1.6; color: #3d3530; }
.briefing-overall-label { font-size: 10px; font-weight: 700; letter-spacing: 0.14em;
  text-transform: uppercase; color: #8b7e74; margin-bottom: 6px; font-family: 'DM Sans', sans-serif; }
.briefing-section { padding: 20px 28px; border-bottom: 1px solid #f1ebde; }
.briefing-section:last-child { border-bottom: none; }
.briefing-section h3 { margin: 0 0 14px; font-family: 'Playfair Display', serif;
  font-size: 18px; font-weight: 600; color: #2c2520; display: flex; align-items: center; gap: 8px; }
.briefing-section h3 .briefing-icon { font-size: 20px; }
.briefing-story { padding: 12px 0; border-top: 1px solid #f6efe3; }
.briefing-story:first-of-type { border-top: none; }
.briefing-story-theme { display: inline-block; font-size: 10px; font-weight: 700;
  letter-spacing: 0.1em; text-transform: uppercase; color: #8b7e74; margin-right: 6px; }
.briefing-story-headline { font-family: 'Playfair Display', serif; font-size: 15px;
  font-weight: 600; color: #2c2520; margin: 0 0 5px; line-height: 1.35; }
.briefing-story-brief { font-family: 'EB Garamond', serif; font-size: 1rem; line-height: 1.6;
  color: #3d3530; margin: 0 0 6px; }
.briefing-story-source { font-size: 11px; color: #8b7e74; }
.briefing-story-source a { color: #2d5040; text-decoration: none; }
.briefing-story-source a:hover { text-decoration: underline; }
.briefing-empty { font-family: 'EB Garamond', serif; font-style: italic; color: #8b7e74; font-size: 0.95rem; }
</style>
"""


def _safe(text: str) -> str:
    return html.escape(text or "", quote=True)


def _category_anchor(category: str) -> str:
    return "briefing-" + category.lower().replace(" ", "-").replace("/", "-")


def render_fragment(ai_results: dict, overall: str, today_human: str) -> str:
    parts = [EMBED_STYLES]
    parts.append('<div class="briefing-report">')

    parts.append('<div class="briefing-header">')
    parts.append('<h2>Daily News Briefing</h2>')
    parts.append(
        f'<div class="briefing-sub">'
        f'<span class="briefing-badge">Updated daily</span>{_safe(today_human)}'
        f' &middot; 10 categories &middot; conversation-ready briefs'
        f'</div>'
    )
    parts.append('</div>')

    parts.append('<div class="briefing-toc">')
    for c in CATEGORIES:
        parts.append(f'<a href="#{_category_anchor(c)}">{CATEGORY_ICON.get(c, "")} {_safe(c)}</a>')
    parts.append('</div>')

    if overall:
        parts.append('<div class="briefing-overall">')
        parts.append('<div class="briefing-overall-label">What everyone is talking about today</div>')
        parts.append(f'<div>{_safe(overall)}</div>')
        parts.append('</div>')

    for category in CATEGORIES:
        parts.append(f'<div class="briefing-section" id="{_category_anchor(category)}">')
        parts.append(
            f'<h3><span class="briefing-icon">{CATEGORY_ICON.get(category, "")}</span>{_safe(category)}</h3>'
        )
        stories = ai_results.get(category, [])
        if not stories:
            parts.append('<div class="briefing-empty">No stories available this cycle.</div>')
        else:
            for story in stories:
                headline = story.get("headline", "Untitled")
                brief = story.get("brief", "")
                source = story.get("source", "")
                url = story.get("url", "")
                theme = story.get("theme", "")
                parts.append('<div class="briefing-story">')
                if category == "Miscellaneous" and theme:
                    parts.append(
                        f'<div><span class="briefing-story-theme">'
                        f'{THEME_ICON.get(theme, "")} {_safe(theme)}</span></div>'
                    )
                parts.append(f'<div class="briefing-story-headline">{_safe(headline)}</div>')
                parts.append(f'<div class="briefing-story-brief">{_safe(brief)}</div>')
                if source and url:
                    parts.append(
                        f'<div class="briefing-story-source">— '
                        f'<a href="{_safe(url)}" target="_blank" rel="noopener noreferrer">'
                        f'{_safe(source)}</a></div>'
                    )
                elif source:
                    parts.append(f'<div class="briefing-story-source">— {_safe(source)}</div>')
                parts.append('</div>')
        parts.append('</div>')

    parts.append('</div>')
    return "".join(parts)


def render_standalone(fragment: str, today_human: str) -> str:
    return (
        f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        f'<title>Daily News Briefing — {_safe(today_human)}</title>'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<link rel="preconnect" href="https://fonts.googleapis.com">'
        f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        f'<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600&family=EB+Garamond:wght@400;500&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">'
        f'<style>body{{margin:0;background:#fdfbf8;padding:24px;font-family:system-ui,sans-serif}}</style>'
        f'</head><body>{fragment}</body></html>'
    )
