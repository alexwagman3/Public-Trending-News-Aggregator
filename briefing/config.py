"""Configuration constants and environment-driven knobs."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


CATEGORIES = [
    "Sports", "Tech", "Business", "Science", "US Politics",
    "Global News", "Gaming", "Social Media", "Pop Culture", "Miscellaneous",
]

MISC_THEMES = ["Weather", "Music", "Archaeology", "Holidays", "Religion", "Other"]

CATEGORY_ICON = {
    "Sports": "🏆", "Tech": "💻", "Business": "📈", "Science": "🔬",
    "US Politics": "🏛️", "Global News": "🌍", "Gaming": "🎮",
    "Social Media": "✨", "Pop Culture": "🎬", "Miscellaneous": "🧭",
}

THEME_ICON = {
    "Weather": "⛅", "Music": "🎵", "Archaeology": "🏺",
    "Holidays": "🎉", "Religion": "🙏", "Other": "💡",
}

REDDIT_SUBS = {
    "Sports": ["sports", "nba", "nfl", "baseball", "hockey", "CFB"],
    "Tech": ["technology"],
    "Business": ["business", "economy", "wallstreetbets"],
    "Science": ["science", "space", "Futurology"],
    "US Politics": ["politics"],
    "Global News": ["worldnews", "news"],
    "Gaming": ["gaming", "Games", "pcgaming"],
    "Social Media": ["popular", "OutOfTheLoop", "socialmedia", "youtube", "TikTokCringe", "Twitter"],
    "Pop Culture": ["movies", "television", "music", "hiphopheads", "popculturechat", "netflix", "DisneyPlus"],
    "Miscellaneous": [
        "weather", "tropicalweather",
        "Music", "listentothis",
        "Archaeology", "history",
        "Christianity", "religion",
        "todayilearned", "interestingasfuck", "MadeMeSmile",
    ],
}

MISC_REDDIT_SUBS = {
    "Weather": ["weather", "tropicalweather"],
    "Music": ["Music", "listentothis"],
    "Archaeology": ["Archaeology", "history"],
    "Holidays": ["todayilearned"],
    "Religion": ["Christianity", "religion"],
    "Other": ["todayilearned", "interestingasfuck", "MadeMeSmile"],
}

RSS_FEEDS = {
    "Sports": [
        "https://www.espn.com/espn/rss/news",
        "https://www.cbssports.com/rss/headlines/",
    ],
    "Tech": [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://arstechnica.com/feed/",
    ],
    "Business": [
        "https://www.cnbc.com/id/10001147/device/rss/rss.html",
        "https://www.marketwatch.com/rss/topstories",
        "https://fortune.com/feed/",
    ],
    "Science": [
        "https://www.sciencedaily.com/rss/all.xml",
        "https://phys.org/rss-feed/",
        "https://www.space.com/feeds/all",
        "https://www.smithsonianmag.com/rss/science-nature/",
    ],
    "US Politics": [
        "https://rss.politico.com/politics.xml",
        "https://www.axios.com/feeds/flagship.rss",
        "https://thehill.com/homenews/feed/",
        "https://feeds.npr.org/1014/rss.xml",
    ],
    "Global News": [
        "https://apnews.com/rss",
        "https://www.reuters.com/world/rss/",
        "https://feeds.npr.org/1001/rss.xml",
    ],
    "Gaming": [
        "https://www.polygon.com/rss/index.xml",
        "https://kotaku.com/rss",
        "https://www.ign.com/rss/articles/feed",
    ],
    "Social Media": [
        "https://mashable.com/feeds/rss/all",
        "https://www.socialmediatoday.com/rss.xml",
        "https://digiday.com/feed/",
        "https://techcrunch.com/category/social/feed/",
        "https://www.adweek.com/feed/",
        "https://techradar.com/rss",
    ],
    "Pop Culture": [
        "https://variety.com/feed/",
        "https://www.billboard.com/feed/",
        "https://www.rollingstone.com/feed/",
        "https://collider.com/feed/",
        "https://deadline.com/feed/",
        "https://www.hollywoodreporter.com/feed/",
        "https://www.thewrap.com/feed/",
    ],
    "Miscellaneous": [
        "https://www.weather.gov/rss_page.php?site_name=alerts",
        "https://www.wunderground.com/rss/articles",
        "https://www.npr.org/rss/rss.php?id=1039",
        "https://pitchfork.com/feed/feed-news/rss",
        "https://www.billboard.com/feed/",
        "https://www.sciencedaily.com/rss/fossils_ruins/archaeology.xml",
        "https://www.smithsonianmag.com/rss/history/",
        "https://www.livescience.com/feeds/archaeology",
        "https://religionnews.com/feed/",
        "https://www.npr.org/rss/rss.php?id=1016",
        "https://www.christianitytoday.com/ct/rss.xml",
        "https://www.atlasobscura.com/feeds/latest",
        "https://www.smithsonianmag.com/rss/latest_articles/",
    ],
}

MISC_RSS_FEEDS = {
    "Weather": [
        "https://www.weather.gov/rss_page.php?site_name=alerts",
        "https://www.wunderground.com/rss/articles",
    ],
    "Music": [
        "https://www.npr.org/rss/rss.php?id=1039",
        "https://pitchfork.com/feed/feed-news/rss",
        "https://www.billboard.com/feed/",
    ],
    "Archaeology": [
        "https://www.sciencedaily.com/rss/fossils_ruins/archaeology.xml",
        "https://www.smithsonianmag.com/rss/history/",
        "https://www.livescience.com/feeds/archaeology",
    ],
    "Holidays": [],
    "Religion": [
        "https://religionnews.com/feed/",
        "https://www.npr.org/rss/rss.php?id=1016",
        "https://www.christianitytoday.com/ct/rss.xml",
    ],
    "Other": [
        "https://www.atlasobscura.com/feeds/latest",
        "https://www.smithsonianmag.com/rss/latest_articles/",
    ],
}

GOOGLE_NEWS_TOPICS = {
    "Sports": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp1ZEdvU0FtVnVHZ0pWVXlnQVAB",
    "Tech": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlnQVAB",
    "Business": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx6TVdZU0FtVnVHZ0pWVXlnQVAB",
    "Science": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRFp0Y1RjU0FtVnVHZ0pWVXlnQVAB",
    "US Politics": "CAAqIQgKIhtDQkFTRGdvSUwyMHZNRFZ4ZERBU0FtVnVLQUFQAQ",
    "Global News": "CAAqJggKIiBDQkFTRWdvSUwyMHZNRFZxYUdjU0FtVnVHZ0pWVXlnQVAB",
}

REQUEST_TIMEOUT = 20
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)

DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"

# 1.0 = pure engagement (favors biggest stories of the week even if a few
# days old). 0.0 = pure recency (favors anything that broke in the last hour).
TRENDING_BIAS = float(os.environ.get("TRENDING_BIAS", "0.50"))
RECENCY_WINDOW_HOURS = 7 * 24
RSS_HARD_CUTOFF_HOURS = 7 * 24
SCORE_NORMALIZATION_CAP = 5000

# Hard cap on themes surfaced in the Miscellaneous category.
MISC_THEME_LIMIT = 3

OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "output")
