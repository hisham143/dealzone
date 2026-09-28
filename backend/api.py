from fastapi import FastAPI, HTTPException

from fastapi.middleware.cors import CORSMiddleware

from database import get_connection

from pathlib import Path

from fastapi.staticfiles import StaticFiles


# ==========================================
# FastAPI Application
# ==========================================

app = FastAPI(
    title="Telegram Deals API",
    description="API for Telegram shopping offers",
    version="1.0.0"
)


# ==========================================
# Media folder
# ==========================================

MEDIA_DIR = Path(__file__).parent / "media"

MEDIA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


app.mount(
    "/media",
    StaticFiles(directory=MEDIA_DIR),
    name="media"
)


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# ==========================================
# Store logo fallback
# ==========================================

STORE_LOGOS = {
    "Amazon": "/media/logos/amazon.png",
    "Flipkart": "/media/logos/flipkart.png",
    "Myntra": "/media/logos/myntra.png",
    "AJIO": "/media/logos/ajio.png",
    "Meesho": "/media/logos/meesho.png",
    "Croma": "/media/logos/croma.png",
    "Tata Cliq": "/media/logos/tatacliq.png",
    "Nykaa": "/media/logos/nykaa.png",
    "Reliance Digital": "/media/logos/reliance-digital.png",
    "FirstCry": "/media/logos/firstcry.png",
    "Decathlon": "/media/logos/decathlon.png",
    "Blinkit": "/media/logos/blinkit.png",
    "Swiggy": "/media/logos/swiggy.png",
    "Zomato": "/media/logos/zomato.png",
}


def get_fallback_image(store):
    """
    Return a local store logo when
    Telegram product images are not used.
    """

    return STORE_LOGOS.get(store)


# ==========================================
# Home
# ==========================================

@app.get("/")
def home():

    return {
        "message": "Telegram Deals API is running",
        "status": "success"
    }


# ==========================================
# Get all active offers
# ==========================================

@app.get("/offers")
def get_offers():

    connection = get_connection()

    offers = connection.execute(
        """
        SELECT
            id,
            telegram_message_id,
            title,
            store,
            discount,
            category,
            description,
            links,
            image_url,
            message_date,
            created_at
        FROM offers

        ORDER BY
            telegram_message_id DESC
        """
    ).fetchall()

    connection.close()

    return {
        "count": len(offers),

        "offers": [

            {
                **dict(offer),

                "fallback_image_url": get_fallback_image(
                    offer["store"]
                )
            }

            for offer in offers
        ]
    }


# ==========================================
# Get latest 10 offers
# ==========================================

@app.get("/offers/latest")
def get_latest_offers():

    connection = get_connection()

    offers = connection.execute(
        """
        SELECT
            id,
            telegram_message_id,
            title,
            store,
            discount,
            category,
            description,
            links,
            image_url,
            message_date,
            created_at

        FROM offers

        ORDER BY
            telegram_message_id DESC

        LIMIT 10
        """
    ).fetchall()

    connection.close()

    return {
        "count": len(offers),

        "offers": [
            dict(offer)
            for offer in offers
        ]
    }


# ==========================================
# Get single offer
# ==========================================

@app.get("/offers/{offer_id}")
def get_offer(offer_id: int):

    connection = get_connection()

    offer = connection.execute(
        """
        SELECT
            id,
            telegram_message_id,
            title,
            store,
            discount,
            category,
            description,
            links,
            image_url,
            message_date,
            created_at

        FROM offers

        WHERE id = ?
        """,
        (offer_id,)
    ).fetchone()

    connection.close()

    if offer is None:

        raise HTTPException(
            status_code=404,
            detail="Offer not found"
        )

    return {
        **dict(offer),

        "fallback_image_url": get_fallback_image(
            offer["store"]
        )
    }


# ==========================================
# Get categories
# ==========================================

@app.get("/categories")
def get_categories():

    connection = get_connection()

    categories = connection.execute(
        """
        SELECT DISTINCT category

        FROM offers

        WHERE category IS NOT NULL

        AND category != ''

        ORDER BY category
        """
    ).fetchall()

    connection.close()

    return {
        "categories": [
            row["category"]
            for row in categories
        ]
    }


# ==========================================
# Get stores
# ==========================================

@app.get("/stores")
def get_stores():

    connection = get_connection()

    stores = connection.execute(
        """
        SELECT DISTINCT store

        FROM offers

        WHERE store IS NOT NULL

        AND store != ''

        ORDER BY store
        """
    ).fetchall()

    connection.close()

    return {
        "stores": [
            row["store"]
            for row in stores
        ]
    }