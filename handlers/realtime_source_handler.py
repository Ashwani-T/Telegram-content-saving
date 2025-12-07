# handlers/realtime_source_handler.py  — use the active client passed in
from telethon import events
from link_parser import extract_bot_links, extract_payload
from bot_trigger import trigger_bot
from config import BOT_USERNAME, SOURCE  # note new helper

async def register_source_handler(client):
    # resolve SOURCE using the active running client (passed in)
    #ENTITY = await resolve_target(client, SOURCE)

    @client.on(events.NewMessage(chats=SOURCE))
    async def source_handler(event):
        msg = event.message
        if not msg or msg.action:
            return

        print("Source message:", msg)
        links = extract_bot_links(msg.text or "")
        print("Found links:", links)
        for link in links:
            payload = extract_payload(link)
            if payload:
                await trigger_bot(client, BOT_USERNAME, payload)
