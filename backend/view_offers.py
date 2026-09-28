import sqlite3

from database import DATABASE_PATH


connection = sqlite3.connect(DATABASE_PATH)
connection.row_factory = sqlite3.Row

offers = connection.execute("""
    SELECT
        id,
        telegram_message_id,
        title,
        store,
        discount,
        category,
        message_date
    FROM offers
    ORDER BY id DESC
""").fetchall()


print("\n" + "=" * 70)
print("📦 SAVED OFFERS")
print("=" * 70)

if not offers:
    print("No offers found.")

else:
    for offer in offers:
        print(f"""
ID          : {offer['id']}
Telegram ID : {offer['telegram_message_id']}
Title       : {offer['title']}
Store       : {offer['store']}
Discount    : {offer['discount']}
Category    : {offer['category']}
Date        : {offer['message_date']}
{"-" * 70}
""")


connection.close()