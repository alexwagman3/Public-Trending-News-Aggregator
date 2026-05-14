# Public Trending News Aggregator

A standalone Python pipeline that builds a daily news briefing from public
feeds (Reddit, Hacker News, RSS, Google News) and uses an LLM to curate the
three most conversation-worthy stories in each of ten categories.

The result is a self-contained HTML page plus a JSON metadata file you can
open in a browser, embed in any site, or deploy as a static page.

## What it does

1. **Aggregates** several hundred candidate stories from ~30 public sources
   over a 7-day rolling window.
2. **Weights** each story by engagement (score, comments) blended with
   recency so a sustained multi-day story beats a fresh blip.
3. **Curates** the top 3 stories per category with DeepSeek, asking the
   model to write two-sentence briefs and avoid repeats across categories.
4. **Renders** an HTML briefing (standalone + embeddable fragment) and a
   JSON metadata file written to `./output/`.

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                  main.py  /  python -m briefing                │
└──────────────┬─────────────────────────────────────────────────┘
               │
   ┌───────────▼───────────┐
   │   briefing/fetchers   │  Reddit · Hacker News · RSS feeds ·
   │                       │  Google News topics · public holidays
   └───────────┬───────────┘
               │  ~200 RawStory objects
               ▼
   ┌───────────────────────┐
   │   briefing/models     │  compute_weight = engagement × recency
   └───────────┬───────────┘
               │  sorted candidates per category
               ▼
   ┌───────────────────────┐
   │   briefing/curator    │  DeepSeek picks top 3 per category +
   │                       │  one item per Miscellaneous theme +
   │                       │  a two-sentence overall summary
   └───────────┬───────────┘
               │
               ▼
   ┌───────────────────────┐
   │   briefing/renderer   │  HTML fragment + standalone page
   └───────────┬───────────┘
               │
               ▼
       output/
         index.html              ← open this in a browser
         briefing-fragment.html  ← embed-only HTML body
         briefing-meta.json      ← updated_iso, story_count, …
```

## Data sources

| Type        | Sources                                                                 |
|-------------|-------------------------------------------------------------------------|
| Reddit      | top-of-week from ~25 subreddits across all 10 categories                |
| Hacker News | the public `beststories` feed                                           |
| RSS         | ~35 mainstream feeds (ESPN, TechCrunch, Reuters, AP, Variety, …)        |
| Google News | curated Google News topic IDs per category                              |
| Holidays    | `date.nager.at` public-holiday API for US / GB / CA                     |

All sources are public and require no API keys. The only key the project
needs is `DEEPSEEK_API_KEY` for LLM curation; without it the pipeline still
runs end-to-end and writes an empty-briefing scaffold so you can see the
shape of the output.

## Setup

```bash
git clone https://github.com/<your-account>/public-trending-news-aggregator
cd public-trending-news-aggregator

python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# edit .env and paste your DEEPSEEK_API_KEY
```

## Environment variables

| Variable            | Required | Default  | Notes                                     |
|---------------------|----------|----------|-------------------------------------------|
| `DEEPSEEK_API_KEY`  | yes\*    | —        | https://platform.deepseek.com/            |
| `TRENDING_BIAS`     | no       | `0.50`   | 1.0 = pure engagement, 0.0 = pure recency |
| `OUTPUT_DIR`        | no       | `output` | Where the HTML / JSON are written         |

\* Without `DEEPSEEK_API_KEY` the script still runs and writes valid output
files, but every category will be empty.

## Run

```bash
python main.py
# or equivalently
python -m briefing
```

A full run takes 3-5 minutes (mostly polite delays between source fetches
plus ~10 DeepSeek calls). When it finishes, open `output/index.html` in a
browser — or serve the folder with the simplest possible static front-end:

```bash
python -m http.server -d output 8000
# then visit http://localhost:8000
```

For automated deploy, point GitHub Pages at the `output/` directory on the
default branch, or copy `output/` into any static host (Netlify, Vercel,
S3, plain nginx). No build step, no framework, no Cloudflare Workers — the
output is just an HTML file and a JSON file.

## Sample output

`output/briefing-meta.json`

```json
{
  "updated_iso": "2026-05-14T09:32:01Z",
  "updated_human": "May 14, 2026",
  "weekday": "Thursday",
  "story_count": 27,
  "category_count": 10
}
```

A single rendered story inside `output/index.html`:

```html
<div class="briefing-section" id="briefing-tech">
  <h3><span class="briefing-icon">💻</span>Tech</h3>
  <div class="briefing-story">
    <div class="briefing-story-headline">
      Major chipmaker unveils next-gen accelerator at developer conference
    </div>
    <div class="briefing-story-brief">
      The new chip targets large-model inference at roughly half the power
      draw of the previous generation. Analysts say availability remains
      the real bottleneck for hyperscaler buyers.
    </div>
    <div class="briefing-story-source">
      — <a href="https://example.com/story" target="_blank"
           rel="noopener noreferrer">techcrunch.com</a>
    </div>
  </div>
  …
</div>
```

## Project layout

```
briefing/
  __init__.py     # main() orchestrator
  __main__.py     # `python -m briefing` entrypoint
  config.py       # categories, sources, env-driven knobs
  models.py       # RawStory + weighting math
  fetchers.py     # Reddit / HN / RSS / Google News / holidays
  curator.py      # DeepSeek prompts + parsing
  renderer.py     # HTML templates
main.py           # convenience entrypoint
requirements.txt
.env.example
```

## License

MIT — see [LICENSE](LICENSE).
