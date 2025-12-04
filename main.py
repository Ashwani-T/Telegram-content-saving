# main.py
import asyncio

from bot_listener import register_bot_media_handler
from handlers.realtime_source_handler import register_source_handler
from config import client
from handlers.realtime_source_handler import *
from bot_listener import *
from handlers.bulk_forward_handler import bulk_forward

async def main():
    await client.start()
    
    print("Client started.")

    print("Modes:")
    print("1) Bulk forward")
    print("2) Realtime mode")
    choice = input("Enter 1 or 2: ")

    if choice == "1":
        n = int(input("How many messages (default 200): ") or 200)
        oldest = input("Oldest → newest? (y/n): ").lower() == "y"
        await bulk_forward(n, oldest)
        await client.disconnect()
        return
    
    await register_source_handler(client)
    register_bot_media_handler(client)


    print("Realtime mode started...")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
