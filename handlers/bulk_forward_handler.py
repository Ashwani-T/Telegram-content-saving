# handlers/bulk_forward_handler.py
from config import client, SOURCE
from forwarder import forward_message

async def bulk_forward(limit=200, oldest_first=True):
    msgs = await client.get_messages(SOURCE, limit=limit)
    if oldest_first:
        msgs = reversed(msgs)

    for m in msgs:
        if not m or m.action:
            continue
        await forward_message(m)
