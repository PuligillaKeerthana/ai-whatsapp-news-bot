import feedparser
from bs4 import BeautifulSoup

# Category to emoji mapping (shared with app.py)
CATEGORY_EMOJIS = {
    "general": "📰",
    "sports": "🏏",
    "tech": "💻",
    "world": "🌍",
    "business": "💼",
    "cinema": "🎬",
    "politics": "🏛️"
}

# RSS Feeds by category
RSS_FEEDS = {
    "general": "https://www.hindustantimes.com/rss/india-news/rssfeed.xml",
    "sports": "https://timesofindia.indiatimes.com/rssfeeds/4719148.cms",
    "tech": "https://timesofindia.indiatimes.com/rssfeeds/5880659.cms",
    "world": "https://feeds.feedburner.com/ndtvnews-world-news",
    "business": "https://timesofindia.indiatimes.com/rssfeeds/1898055.cms",
    "cinema": "https://timesofindia.indiatimes.com/rssfeeds/1081479906.cms",
    "politics": "https://www.hindustantimes.com/rss/india-news/rssfeed.xml"
}

def clean_summary(summary):
    soup = BeautifulSoup(summary, "html.parser")
    return soup.get_text(strip=True)

def fetch_rss_news(categories=None):
    """
    Fetch top 10 news from selected (or all) categories.
    """
    if categories is None or not categories:
        categories = list(RSS_FEEDS.keys())  # Default to all categories

    selected_feeds = [RSS_FEEDS[cat] for cat in categories if cat in RSS_FEEDS]
    all_articles = []

    for rss_url in selected_feeds:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:5]:
            summary = clean_summary(entry.summary) if 'summary' in entry and entry.summary.strip() else "No summary available."
            all_articles.append({
                "title": entry.title,
                "link": entry.link,
                "summary": summary
            })

    if not all_articles and categories != list(RSS_FEEDS.keys()):
        return fetch_rss_news(categories=list(RSS_FEEDS.keys()))

    return sorted(all_articles, key=lambda x: x["title"])[:10]

# Optional: Run this file directly to test output
if __name__ == "__main__":
    selected_categories = []  # Empty = all categories
    news = fetch_rss_news(selected_categories)

    # Show category emojis
    emoji_line = " | ".join(f"{CATEGORY_EMOJIS.get(cat, '')} {cat.capitalize()}" for cat in selected_categories or RSS_FEEDS.keys())
    print(f"\n📂 Selected Categories: {emoji_line}\n")

    # Print news
    for idx, article in enumerate(news, 1):
        print(f"{idx}. {article['title']}")
        print(f"🔗 {article['link']}")
        print(f"📝 Summary: {article['summary']}\n")
