import os
import asyncio

from dotenv import load_dotenv
from telethon import TelegramClient


load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")


client = TelegramClient(
    "deal_listener",
    API_ID,
    API_HASH
)


async def main():

    print("🔍 Searching your Telegram channels...")
    print()

    await client.start()

    found = 0

    async for dialog in client.iter_dialogs():

        entity = dialog.entity

        title = getattr(entity, "title", "") or ""
        username = getattr(entity, "username", None)
        entity_id = getattr(entity, "id", None)

        search_text = (
            f"{title} {username or ''}"
        ).lower()

        if (
            "loot" in search_text
            or "magix" in search_text
            or "magi" in search_text
        ):

            found += 1

            print("=" * 60)
            print("📡 POSSIBLE CHANNEL FOUND")
            print("=" * 60)

            print("Title     :", title)
            print("Username  :", username)
            print("Channel ID:", entity_id)
            print("Dialog    :", dialog.name)

            print("=" * 60)
            print()

    print()
    print("✅ Search completed.")
    print("📦 Matching dialogs:", found)

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())