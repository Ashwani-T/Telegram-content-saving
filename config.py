# config.py
import os
import logging
from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("forwarder")

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION = os.getenv("SESSION", "session")
SOURCE = os.getenv("SOURCE")
TARGET = os.getenv("TARGET")
DB_PATH = os.getenv("DB_PATH", "forwarded.db")
BOT_USERNAME=os.getenv("BOT_USERNAME")


async def resolve_target(tg_id):
    try:
        if tg_id.lstrip("-").isdigit():
            return await client.get_entity(int(tg_id))
        
        TARGET_ENTITY = await client.get_entity(tg_id)

        return TARGET_ENTITY
    
    except Exception as e:
        log.error(f"Cannot resolve target: {e}")
        raise
    
    


client = TelegramClient(SESSION, API_ID, API_HASH)


