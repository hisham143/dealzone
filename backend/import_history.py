import os
import json
import asyncio

from dotenv import load_dotenv
from telethon import TelegramClient

from database import create_database, save_offer
from offer_parser import parse_offer


load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")


client = TelegramClient(
    "deal_listener",
    API_ID,
    API_HASH
)


async def import_history():

    create_database()

    print("🚀 Starting Telegram history import...")
    print("📡 Channel:", CHANNEL)

    await client.start()

    print("✅ Telegram connected!")
    print("📥 Fetching previous offers...")

    messages = await client.get_messages(
        CHANNEL,
        limit=50
    )

    saved_count = 0

    for message in reversed(messages):

        text = message.text or ""

        if not text.strip():
            continue

        offer = parse_offer(text)

        links_json = json.dumps(
            offer["links"],
            ensure_ascii=False
        )

        save_offer(
            telegram_message_id=message.id,
            title=offer["title"],
            store=offer["store"],
            discount=offer["discount"],
            category=offer["category"],
            description=offer["description"],
            links=links_json,
            image_url=None,
            message_date=str(message.date)
        )

        saved_count += 1

        print(
            f"✅ Imported #{message.id} | "
            f"{offer['store']} | "
            f"{offer['title'][:60]}"
        )

    print()
    print("=" * 60)
    print(f"🎉 Import completed!")
    print(f"📦 Messages processed: {len(messages)}")
    print(f"💾 Offers processed: {saved_count}")
    print("=" * 60)

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(import_history())