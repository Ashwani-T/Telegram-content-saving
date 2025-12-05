# config.py  — safer variant
import os
import logging
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("forwarder")

# --- required envs ---
_api_id = os.getenv("API_ID")
_api_hash = os.getenv("API_HASH")

if not _api_id or not _api_hash:
    raise RuntimeError("Please set API_ID and API_HASH in your .env (export API_ID, API_HASH)")

try:
    API_ID = int(_api_id)
except ValueError:
    raise RuntimeError("API_ID must be an integer in .env")

API_HASH = _api_hash
SESSION = os.getenv("SESSION", "session")
SOURCE = os.getenv("SOURCE")
TARGET = os.getenv("TARGET")
DB_PATH = os.getenv("DB_PATH", "forwarded.db")
BOT_USERNAME = os.getenv("BOT_USERNAME")

# Create client object. It is safe to import this module at startup.
client = TelegramClient(SESSION, API_ID, API_HASH)

# Prefer resolving using the active client passed by code, but keep helper as fallback
async def resolve_target(client_obj, tg_id):
    try:
        if isinstance(tg_id, (int,)) or (isinstance(tg_id, str) and tg_id.lstrip("-").isdigit()):
            return await client_obj.get_entity(int(tg_id))
        return await client_obj.get_entity(tg_id)
    except Exception as e:
        log.error(f"Cannot resolve target '{tg_id}': {e}")
        raise
