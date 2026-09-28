import os
import json
import asyncio

from pathlib import Path
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from telethon import TelegramClient, events

from database import (
    create_database,
    save_offer,
    get_connection,
    cleanup_expired_offers
)

from offer_parser import parse_offer


# ==========================================
# Load environment variables
# ==========================================

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
CHANNEL = int(os.getenv("TELEGRAM_CHANNEL"))


# ==========================================
# Telegram client
# ==========================================

client = TelegramClient(
    "deal_listener",
    API_ID,
    API_HASH
)


# ==========================================
# Check if message is within 2 days
# ==========================================

def is_within_2_days(message_date):
    """
    Return True only if the Telegram message
    was received within the last 2 days.
    """

    if message_date.tzinfo is None:
        message_date = message_date.replace(
            tzinfo=timezone.utc
        )

    cutoff_time = (
        datetime.now(timezone.utc)
        - timedelta(days=2)
    )

    return message_date >= cutoff_time


# ==========================================
# Save Telegram offer
# ==========================================

async def save_telegram_offer(message):
    """
    Parse Telegram message, filter old/non-product
    offers and save the offer to SQLite.

    Telegram images are NOT downloaded.
    """

    # --------------------------------------
    # Ignore messages older than 2 days
    # --------------------------------------

    if not is_within_2_days(message.date):

        print(
            f"⏳ Message {message.id} is older than 2 days. Skipping."
        )

        return

    text = message.text or ""

    # --------------------------------------
    # Ignore messages without text
    # --------------------------------------

    if not text.strip():

        print(
            "⚠️ Message has no text. Skipping."
        )

        return

    # --------------------------------------
    # Parse Telegram message
    # --------------------------------------

    offer = parse_offer(text)

    # --------------------------------------
    # Filter non-product offers
    # --------------------------------------

    if offer["is_non_product"]:

        print()
        print("=" * 60)
        print("🚫 NON-PRODUCT OFFER SKIPPED")
        print("=" * 60)

        print(
            "Message ID :",
            message.id
        )

        print(
            "Title      :",
            offer["title"]
        )

        print(
            "Category   :",
            offer["category"]
        )

        print("=" * 60)

        return

    # --------------------------------------
    # Product image
    # --------------------------------------

    # Telegram images are intentionally NOT downloaded.
    # Website will use its own image/placeholder system.

    image_url = None

    # --------------------------------------
    # Prepare links
    # --------------------------------------

    links_json = json.dumps(
        offer["links"],
        ensure_ascii=False
    )

    # --------------------------------------
    # Save offer to database
    # --------------------------------------

    save_offer(

        telegram_message_id=message.id,

        title=offer["title"],

        store=offer["store"],

        discount=offer["discount"],

        category=offer["category"],

        description=offer["description"],

        links=links_json,

        image_url=image_url,

        message_date=str(message.date)
    )

    # --------------------------------------
    # Print saved offer
    # --------------------------------------

    print()
    print("=" * 60)
    print("🔥 NEW OFFER SAVED")
    print("=" * 60)

    print(
        "Message ID :",
        message.id
    )

    print(
        "Title      :",
        offer["title"]
    )

    print(
        "Store      :",
        offer["store"]
    )

    print(
        "Discount   :",
        offer["discount"]
    )

    print(
        "Category   :",
        offer["category"]
    )

    print(
        "Price      :",
        offer["price"]
    )

    print(
        "Brand      :",
        offer["brand"]
    )

    print(
        "Links      :",
        len(offer["links"])
    )

    print(
        "Image      :",
        "Disabled"
    )

    print("=" * 60)


# ==========================================
# Get latest saved Telegram message ID
# ==========================================

def get_latest_saved_message_id():

    connection = get_connection()

    result = connection.execute(
        """
        SELECT MAX(telegram_message_id)
        FROM offers
        """
    ).fetchone()

    connection.close()

    if result[0] is None:
        return 0

    return result[0]


# ==========================================
# Sync missed Telegram offers
# ==========================================

async def sync_missed_offers():

    latest_saved_id = (
        get_latest_saved_message_id()
    )

    print()
    print(
        "🔄 Checking for missed Telegram offers..."
    )

    print(
        "📌 Latest saved message ID:",
        latest_saved_id
    )

    # --------------------------------------
    # Get latest Telegram message
    # --------------------------------------

    latest_message = await client.get_messages(
        CHANNEL,
        limit=1
    )

    if latest_message:

        latest_telegram_message = (
            latest_message[0]
        )

        print(
            "📡 Latest Telegram message ID:",
            latest_telegram_message.id
        )

        print(
            "📅 Latest Telegram message date:",
            latest_telegram_message.date
        )

        latest_text = (
            latest_telegram_message.text or ""
        )

        print(
            "📝 Latest Telegram message:",
            latest_text[:150]
        )

    # --------------------------------------
    # Fetch missed messages
    # --------------------------------------

    missed_count = 0

    async for message in client.iter_messages(
        CHANNEL,
        min_id=latest_saved_id
    ):

        if message.id <= latest_saved_id:
            continue

        # Stop when messages become older than 2 days

        if not is_within_2_days(message.date):

            print(
                "⏳ Reached messages older than 2 days."
            )

            break

        print()
        print(
            f"📥 Missed message found: {message.id}"
        )

        await save_telegram_offer(
            message
        )

        missed_count += 1

    # --------------------------------------
    # Sync completed
    # --------------------------------------

    print()

    print(
        "✅ Missed offer sync completed."
    )

    print(
        "📦 Offers checked:",
        missed_count
    )

    print()


# ==========================================
# Automatic cleanup loop
# ==========================================

async def cleanup_loop():

    print(
        "🧹 Automatic 2-day cleanup started."
    )

    while True:

        try:

            deleted_count = (
                cleanup_expired_offers()
            )

            if deleted_count > 0:

                print(
                    f"🧹 Removed {deleted_count} expired offers."
                )

            else:

                print(
                    "✅ Cleanup check complete. "
                    "No expired offers."
                )

        except Exception as e:

            print(
                f"⚠️ Cleanup error: {e}"
            )

        # Check every 1 minute

        await asyncio.sleep(60)


# ==========================================
# Listen for NEW Telegram messages
# ==========================================

@client.on(
    events.NewMessage(chats=CHANNEL)
)
async def new_offer(event):

    print()

    print(
        "📩 New Telegram message received!"
    )

    await save_telegram_offer(
        event.message
    )


# ==========================================
# Main
# ==========================================

async def main():

    # --------------------------------------
    # Create database if needed
    # --------------------------------------

    create_database()

    print(
        "🚀 Starting Telegram Deal Listener..."
    )

    # --------------------------------------
    # Telegram login
    # --------------------------------------

    await client.start()

    print(
        "✅ Telegram connected successfully!"
    )

    print(
        "📡 Channel:",
        CHANNEL
    )

    # --------------------------------------
    # Remove existing expired offers
    # --------------------------------------

    print()

    print(
        "🧹 Running initial 2-day cleanup..."
    )

    cleanup_expired_offers()

    # --------------------------------------
    # Check missed messages
    # --------------------------------------

    await sync_missed_offers()

    # --------------------------------------
    # Start automatic cleanup
    # --------------------------------------

    asyncio.create_task(
        cleanup_loop()
    )

    # --------------------------------------
    # Start waiting for new offers
    # --------------------------------------

    print()

    print(
        "📡 Waiting for new offers..."
    )

    print(
        "⏱️ Cleanup interval: 1 minute"
    )

    print(
        "⏳ Offer lifetime: 2 days"
    )

    print(
        "🖼️ Telegram image download: Disabled"
    )

    print()

    # --------------------------------------
    # Keep listener alive
    # --------------------------------------

    await client.run_until_disconnected()


# ==========================================
# Start application
# ==========================================

if __name__ == "__main__":

    asyncio.run(main())