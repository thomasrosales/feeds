import feedparser


def parse_rss_to_dict(rss_content: str) -> dict:
    return feedparser.parse(rss_content)


def xml_is_present(rss_headers: dict) -> bool:
    return "xml" in rss_headers
