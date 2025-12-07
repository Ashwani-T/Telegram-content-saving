# main.py

from bot_listener import register_bot_media_handler
from handlers.realtime_source_handler import register_source_handler
from config import client
from handlers.bulk_forward_handler import bulk_forward

async def main():
    await client.start()
    
    print("Client started.")
    print(" Realtime mode")
        
    register_source_handler(client)
    register_bot_media_handler(client)


    print("Realtime mode started...")
    await client.run_until_disconnected()

if __name__ == "__main__":
	import asyncio
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())

