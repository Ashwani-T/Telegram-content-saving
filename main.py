# main.py

from bot_listener import register_bot_media_handler
from config import client, SOURCE
from handlers.channel_poller import poll_channel_updates


async def main():
    await client.start()
    
    print("Client started.")
    print(" Realtime mode")

    register_bot_media_handler(client)
    asyncio.create_task(poll_channel_updates(client, SOURCE))


    print("Realtime mode started...")
    await client.run_until_disconnected()

if __name__ == "__main__":
	import asyncio
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())

