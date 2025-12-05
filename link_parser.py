# link_parser.py  — fixed
import re
from urllib.parse import urlparse, parse_qs

telegram_link_regex = re.compile(r'https?://t\.me/[^\s]+')

def extract_bot_links(text: str):
    """Return full t.me links found in text (strings)."""
    if not text:
        return []
    links = telegram_link_regex.findall(text)
    return links

def extract_payload(link: str):
    """Return the `start` payload from a t.me bot deep link, or None."""
    try:
        parsed = urlparse(link)
        query = parse_qs(parsed.query)
        return query.get("start", [None])[0]
    except Exception:
        return None
