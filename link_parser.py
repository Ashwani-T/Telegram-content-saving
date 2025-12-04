# link_parser.py
import re
from urllib.parse import urlparse, parse_qs

telegram_link_regex = re.compile(r'https?://t\.me/[^\s]+')

def extract_bot_links(text: str):
    """Extract deep links like https://t.me/Bot?start=xyz"""
    links = telegram_link_regex.findall(text)
    bot_links = []

    for link in links:
        parsed = urlparse(link)
        bot_name = parsed.path.strip("/")
        query = parse_qs(parsed.query)

        if "start" in query:
            payload = query["start"][0]
            bot_links.append((payload))

    return bot_links

def extract_payload(link: str):
    """
    Extracts the payload from bot links like:
    https://t.me/sakshiibot?start=XYZ123
    """
    try:
        parsed = urllib.parse.urlparse(link)
        query = urllib.parse.parse_qs(parsed.query)

        if "start" in query:
            return query["start"][0]

        return None
    except Exception:
        return None

