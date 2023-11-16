import feedparser


def parse_rss_to_dict(rss_content: str) -> dict:
    """
    If the rss_content is an invalid rss xml format
    the result will contain the same structure as
    if it was a valid format, therefore when the backend
    models process the "entries" key it wil contain an empty
    list.
    """
    return feedparser.parse(rss_content)


def xml_is_present(rss_headers: dict) -> bool:
    return "xml" in rss_headers
