import sqlite3
from pathlib import Path
from datetime import datetime, timedelta, timezone

DATABASE_PATH = Path(__file__).parent / "offers.db"
MEDIA_DIR = Path(__file__).parent / "media" / "offers"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_database():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS offers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_message_id INTEGER UNIQUE,
            title TEXT,
            store TEXT,
            discount TEXT,
            category TEXT,
            description TEXT,
            links TEXT,
            image_url TEXT,
            message_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def save_offer(
    telegram_message_id,
    title,
    store,
    discount,
    category,
    description,
    links,
    image_url,
    message_date
):
    connection = get_connection()

    connection.execute("""
        INSERT OR IGNORE INTO offers (
            telegram_message_id,
            title,
            store,
            discount,
            category,
            description,
            links,
            image_url,
            message_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        telegram_message_id,
        title,
        store,
        discount,
        category,
        description,
        links,
        image_url,
        message_date
    ))

    connection.commit()
    connection.close()


def cleanup_expired_offers():
    """
    Delete offers older than 2 days
    and remove their associated image files.
    """

    cutoff_time = datetime.now(timezone.utc) - timedelta(days=2)

    connection = get_connection()

    rows = connection.execute("""
        SELECT id, telegram_message_id, image_url, message_date
        FROM offers
    """).fetchall()

    expired_ids = []

    for row in rows:
        try:
            message_date = datetime.fromisoformat(row["message_date"])

            # Convert naive datetime to UTC if necessary
            if message_date.tzinfo is None:
                message_date = message_date.replace(tzinfo=timezone.utc)

            if message_date < cutoff_time:
                expired_ids.append(row["id"])

                # Delete associated image
                image_url = row["image_url"]

                if image_url:
                    image_path = Path(__file__).parent / image_url.lstrip("/")

                    if image_path.exists():
                        try:
                            image_path.unlink()
                            print(
                                f"🗑️ Image deleted: {image_path.name}"
                            )
                        except Exception as e:
                            print(
                                f"⚠️ Could not delete image "
                                f"{image_path}: {e}"
                            )

        except Exception as e:
            print(
                f"⚠️ Could not process offer "
                f"{row['telegram_message_id']}: {e}"
            )

    # Delete expired database records
    if expired_ids:
        connection.executemany(
            "DELETE FROM offers WHERE id = ?",
            [(offer_id,) for offer_id in expired_ids]
        )

        connection.commit()

    connection.close()

    if expired_ids:
        print(
            f"🧹 Cleanup complete: "
            f"{len(expired_ids)} expired offers removed."
        )

    return len(expired_ids)


if __name__ == "__main__":
    create_database()
    print("✅ Database created successfully!")