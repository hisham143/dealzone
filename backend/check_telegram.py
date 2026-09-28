import os
import asyncio

from dotenv import load_dotenv
from telethon import TelegramClient


# ==========================================
# Load environment variables
# ==========================================

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
CHANNEL = os.getenv("TELEGRAM_CHANNEL")


# ==========================================
# Telegram client
# ==========================================

client = TelegramClient(
    "deal_listener",
    API_ID,
    API_HASH
)


async def main():

    print("🔍 Checking Telegram channel...")
    print()

    # Connect to Telegram
    await client.start()

    print("✅ Telegram connected")
    print()

    # Get channel
    entity = await client.get_entity(CHANNEL)

    print("=" * 60)
    print("📡 CHANNEL INFORMATION")
    print("=" * 60)

    print("Title    :", entity.title)
    print("Username :", getattr(entity, "username", None))
    print("Channel ID:", entity.id)

    print("=" * 60)
    print()

    # Get latest 10 messages
    messages = await client.get_messages(
        entity,
        limit=10
    )

    print("📝 LATEST 10 TELEGRAM MESSAGES")
    print("=" * 60)

    for message in messages:

        text = message.text or ""

        print()
        print("Message ID :", message.id)
        print("Date       :", message.date)
        print("Has Photo  :", bool(message.photo))
        print("Text       :", text[:200])
        print("-" * 60)

    print()
    print("✅ Telegram check completed.")

    await client.disconnect()


# ==========================================
# Run
# ==========================================

if __name__ == "__main__":
    asyncio.run(main())