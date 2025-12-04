# handlers/bot_media_handler.py

from telethon import events
from forwarder import forward_message
from config import BOT_USERNAME   # you must add this in .env

def register_bot_media_handler(client):
    @client.on(events.NewMessage(chats=BOT_USERNAME))
    async def bot_media(event):
        msg = event.message

        if not msg or msg.action:
            return

        # Only forward messages that have media
        if msg.media:
            await forward_message(msg)
