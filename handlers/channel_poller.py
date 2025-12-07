import asyncio
from telethon import functions, types

from link_parser import extract_bot_links, extract_payload
from bot_trigger import trigger_bot
from config import BOT_USERNAME


async def poll_channel_updates(client, source):
    """
    Polls channel every 5 seconds using GetMessagesRequest.
    Works even if Telegram push updates fail.
    """

    # Resolve channel → InputPeerChannel
    entity = await client.get_entity(source)
    channel = types.InputPeerChannel(entity.id, entity.access_hash)

    last_id =29263

    while True:
        try:
            # Request latest messages
            history = await client(
                functions.messages.GetHistoryRequest(
                    peer=channel,
                    limit=20,
                    offset_id=0,
                    offset_date=None,
                    add_offset=0,
                    max_id=0,
                    min_id=0,
                    hash=0
                )
            )

            for msg in reversed(history.messages):  # oldest → newest
                
                if msg.id > last_id:
                    last_id = msg.id

                    text = msg.message or ""
                    links = extract_bot_links(text)

                    for link in links:
                        payload = extract_payload(link)
                        if payload:
                            await trigger_bot(client, BOT_USERNAME, payload)

        except Exception as e:
            print("[Poller error]:", e)

        await asyncio.sleep(60)  # polling interval
