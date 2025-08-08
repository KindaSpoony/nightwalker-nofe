from typing import List, Dict
import feedparser
import re

def _clean_text(s: str) -> str:
    s = re.sub(r'<[^>]+>', ' ', s or '')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def fetch_rss(feeds: List[str], max_items_per_feed: int = 5) -> List[Dict]:
    items = []
    for url in feeds:
        parsed = feedparser.parse(url)
        for entry in parsed.entries[:max_items_per_feed]:
            published = entry.get("published", "") or entry.get("updated", "")
            source = parsed.feed.get("title", url)
            items.append({
                "title": _clean_text(entry.get("title", "")),
                "link": entry.get("link", ""),
                "published": published,
                "source": source,
                "summary": _clean_text(entry.get("summary", entry.get("description", ""))),
            })
    return items
