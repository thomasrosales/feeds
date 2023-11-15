import feedparser


def parse_feed_to_dict(rss_content: str) -> dict:
    return feedparser.parse(rss_content)
