import feedparser


def xml_to_dict(rss_content: str):
    return feedparser.parse(rss_content)
