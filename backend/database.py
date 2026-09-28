import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

MEDIA_DIR = Path(__file__).parent / "media" / "offers"


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not configured. "
            "Add it to the backend .env file."
        )

    connection = psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    )

    return connection


def create_database():
    """
    Verify that the offers table exists in PostgreSQL.

    The table itself is created in Supabase SQL Editor.
    """

    connection = get_connection()

    try:
        connection.execute("SELECT 1 FROM offers LIMIT 1")
        print("✅ PostgreSQL database connection successful.")
        print("✅ 'offers' table is available.")
    finally:
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

    try:
        connection.execute(
            """
            INSERT INTO offers (
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (telegram_message_id) DO NOTHING
            """,
            (
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
        )

        connection.commit()

    finally:
        connection.close()


def cleanup_expired_offers():
    """
    Delete offers older than 2 days.

    Telegram images are currently disabled, so there
    should normally be no image files to remove.
    """

    cutoff_time = datetime.now(timezone.utc) - timedelta(days=2)

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT id, telegram_message_id, image_url
            FROM offers
            WHERE message_date < %s
            """,
            (cutoff_time,)
        ).fetchall()

        expired_ids = [row["id"] for row in rows]

        # Remove any associated local image files if they exist.
        # Currently image downloading is disabled.
        for row in rows:
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

        if expired_ids:
            connection.execute(
                """
                DELETE FROM offers
                WHERE id = ANY(%s)
                """,
                (expired_ids,)
            )

            connection.commit()

            print(
                f"🧹 Cleanup complete: "
                f"{len(expired_ids)} expired offers removed."
            )

        return len(expired_ids)

    finally:
        connection.close()


if __name__ == "__main__":
    create_database()