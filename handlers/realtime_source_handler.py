# handlers/realtime_source_handler.py
from telethon import events

from link_parser import extract_bot_links, extract_payload
from bot_trigger import trigger_bot
from config import BOT_USERNAME, SOURCE, resolve_target


async def register_source_handler(client):

    ENTITY=await resolve_target(SOURCE)
    @client.on(events.NewMessage(chats=ENTITY))
    async def source_handler(event):
        msg = event.message
        if not msg or msg.action:
            return

        print(msg)
        links = extract_bot_links(msg.text or "")
        print(links)
        for link in links:
            # payload = extract_payload(link)
            await trigger_bot(client, BOT_USERNAME, link)
