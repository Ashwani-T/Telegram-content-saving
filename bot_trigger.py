# bot_trigger.py
from config import client

async def trigger_bot(client, bot_username, payload):
    try:
        await client.send_message(bot_username, f"/start {payload}")
    except Exception as e:
        print("Trigger error:", e)
