import re


# ============================================================
# LINK EXTRACTION
# ============================================================

def extract_links(text):
    """
    Extract URLs from Telegram message text.
    """

    if not text:
        return []

    urls = re.findall(
        r'https?://[^\s<>"\']+',
        text
    )

    # Remove trailing punctuation
    cleaned_urls = []

    for url in urls:
        url = url.rstrip(".,;:!?)]}")

        if url not in cleaned_urls:
            cleaned_urls.append(url)

    return cleaned_urls


# ============================================================
# DISCOUNT EXTRACTION
# ============================================================

def extract_discount(text):
    """
    Extract discount percentage from text.
    """

    if not text:
        return None

    patterns = [
        r'up\s*to\s*(\d{1,3})\s*%\s*off',
        r'flat\s*(\d{1,3})\s*%\s*off',
        r'(\d{1,3})\s*%\s*off',
        r'(\d{1,3})\s*%\s*discount',
        r'(\d{1,3})\s*%\s*save',
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return f"{match.group(1)}% OFF"

    return None


# ============================================================
# PRICE EXTRACTION
# ============================================================

def extract_price(text):
    """
    Extract common Indian prices such as:
    ₹698
    ₹1,299
    Rs. 999
    Rs 999
    INR 999
    """

    if not text:
        return None

    patterns = [
        r'₹\s*([\d,]+)',
        r'Rs\.?\s*([\d,]+)',
        r'INR\s*([\d,]+)',
    ]

    prices = []

    for pattern in patterns:
        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        for price in matches:
            try:
                numeric_price = int(
                    price.replace(",", "")
                )

                # Ignore unrealistic numbers
                if 1 <= numeric_price <= 10000000:
                    prices.append(numeric_price)

            except ValueError:
                pass

    if not prices:
        return None

    return f"₹{min(prices):,}"


# ============================================================
# STORE DETECTION
# ============================================================

def detect_store(text):
    """
    Detect shopping platform/store from text and URLs.

    Store detection works from both:
    - Store name in Telegram text
    - Store/domain present in URLs
    """

    if not text:
        return "Other"

    text_lower = text.lower()

    store_patterns = {

        # ----------------------------------------------------
        # Amazon
        # ----------------------------------------------------
        "Amazon": [
            "amazon.in",
            "amzn.to",
            "amazon.com",
            "amazon",
        ],

        # ----------------------------------------------------
        # Flipkart
        # ----------------------------------------------------
        "Flipkart": [
            "flipkart.com",
            "fkrt.cc",
            "fkrt.it",
            "flipkart",
        ],

        # ----------------------------------------------------
        # Myntra
        # ----------------------------------------------------
        "Myntra": [
            "myntra.com",
            "myntr.in",
            "myntra",
        ],

        # ----------------------------------------------------
        # AJIO
        # ----------------------------------------------------
        "AJIO": [
            "ajio.com",
            "ajio",
        ],

        # ----------------------------------------------------
        # Meesho
        # ----------------------------------------------------
        "Meesho": [
            "meesho.com",
            "meesho",
        ],

        # ----------------------------------------------------
        # Croma
        # ----------------------------------------------------
        "Croma": [
            "croma.com",
            "croma",
        ],

        # ----------------------------------------------------
        # Tata Cliq
        # ----------------------------------------------------
        "Tata Cliq": [
            "tatacliq.com",
            "tata cliq",
        ],

        # ----------------------------------------------------
        # Nykaa
        # ----------------------------------------------------
        "Nykaa": [
            "nykaa.com",
            "nykaa",
        ],

        # ----------------------------------------------------
        # Reliance Digital
        # ----------------------------------------------------
        "Reliance Digital": [
            "reliancedigital.in",
            "reliance digital",
        ],

        # ----------------------------------------------------
        # FirstCry
        # ----------------------------------------------------
        "FirstCry": [
            "firstcry.com",
            "firstcry",
        ],

        # ----------------------------------------------------
        # Decathlon
        # ----------------------------------------------------
        "Decathlon": [
            "decathlon.in",
            "decathlon",
        ],

        # ----------------------------------------------------
        # Blinkit
        # ----------------------------------------------------
        "Blinkit": [
            "blinkit.com",
            "blinkit",
        ],

        # ----------------------------------------------------
        # Swiggy
        # ----------------------------------------------------
        "Swiggy": [
            "swiggy.com",
            "swiggy",
        ],

        # ----------------------------------------------------
        # Zomato
        # ----------------------------------------------------
        "Zomato": [
            "zomato.com",
            "zomato",
        ],
    }

    # Check URL/store patterns
    for store, patterns in store_patterns.items():

        for pattern in patterns:

            if pattern in text_lower:
                return store

    return "Other"


# ============================================================
# BRAND DETECTION
# ============================================================

def detect_brand(text):
    """
    Detect common product brands.
    """

    if not text:
        return None

    text_lower = text.lower()

    brands = [
        "boAt",
        "Noise",
        "Boult",
        "JBL",
        "Sony",
        "Samsung",
        "Apple",
        "OnePlus",
        "Xiaomi",
        "Redmi",
        "Realme",
        "Oppo",
        "Vivo",
        "Motorola",
        "Nothing",
        "Google",
        "Philips",
        "LG",
        "HP",
        "Dell",
        "Lenovo",
        "Asus",
        "Acer",
        "Canon",
        "Nikon",
        "Puma",
        "Nike",
        "Adidas",
        "HRX",
        "Levi's",
        "Wildcraft",
        "Fastrack",
        "Titan",
        "Casio",
        "L'Oréal",
        "Lakme",
        "Mamaearth",
        "Minimalist",
    ]

    for brand in brands:

        if brand.lower() in text_lower:
            return brand

    return None


# ============================================================
# CATEGORY DETECTION
# ============================================================

def detect_category(text):
    """
    Detect product category using priority-based keyword matching.
    More specific product categories are checked before broader ones.
    """

    if not text:
        return "Other"

    text_lower = text.lower()

    # ------------------------------------------------------------
    # Beauty
    # ------------------------------------------------------------

    beauty_keywords = [
        "hair oil",
        "hair serum",
        "body lotion",
        "body wash",
        "face wash",
        "facewash",
        "cleanser",
        "shampoo",
        "conditioner",
        "kajal",
        "eyeliner",
        "lipstick",
        "lip balm",
        "foundation",
        "concealer",
        "mascara",
        "serum",
        "moisturizer",
        "moisturiser",
        "sunscreen",
        "perfume",
        "fragrance",
        "deodorant",
        "toner",
        "skincare",
        "makeup",
        "cosmetics",
        "beauty",
    ]

    # ------------------------------------------------------------
    # Fashion
    # ------------------------------------------------------------

    fashion_keywords = [
        "t-shirt",
        "tshirt",
        "shirt",
        "jeans",
        "trouser",
        "pants",
        "jacket",
        "hoodie",
        "coat",
        "dress",
        "kurti",
        "saree",
        "sandal",
        "sandals",
        "shoe",
        "shoes",
        "sneaker",
        "sneakers",
        "slipper",
        "backpack",
        "rucksack",
        "handbag",
        "luggage",
        "travel bag",
        "duffle bag",
        "duffel bag",
        "wallet",
        "belt",
        "jewellery",
        "jewelry",
        "cap",
        "caps",
        "fashion",
        "clothing",
        "apparel",
    ]

    # ------------------------------------------------------------
    # Grocery
    # ------------------------------------------------------------

    grocery_keywords = [
        "moringa",
        "whey protein",
        "protein powder",
        "chips",
        "snack",
        "namkeen",
        "noodles",
        "pasta",
        "biscuit",
        "chocolate",
        "rice",
        "atta",
        "flour",
        "spice",
        "masala",
        "pickle",
        "dry fruit",
        "dry fruits",
        "nuts",
        "juice",
        "coffee",
        "tea",
        "grocery",
        "food",
        "cereal",
        "oats",
        "honey",
        "sugar",
        "salt",
    ]

    # ------------------------------------------------------------
    # Home & Kitchen
    # ------------------------------------------------------------

    home_keywords = [
        "lunch box",
        "pressure cooker",
        "cookware",
        "mixer",
        "grinder",
        "tawa",
        "pan",
        "bottle",
        "kitchen",
        "bedsheet",
        "pillow",
        "curtain",
        "chair",
        "table",
        "storage",
        "cleaning",
        "vacuum",
        "home appliance",
        "home & kitchen",
    ]

    # ------------------------------------------------------------
    # Kids
    # ------------------------------------------------------------

    kids_keywords = [
        "toy",
        "toys",
        "kids",
        "baby",
        "baby product",
        "diaper",
        "school bag",
        "learning toy",
    ]

    # ------------------------------------------------------------
    # Sports
    # ------------------------------------------------------------

    sports_keywords = [
        "cricket",
        "football",
        "badminton",
        "tennis",
        "gym",
        "fitness",
        "sports",
        "running",
        "yoga",
        "dumbbell",
    ]

    # ------------------------------------------------------------
    # Automotive
    # ------------------------------------------------------------

    automotive_keywords = [
        "car charger",
        "car accessory",
        "bike accessory",
        "motorcycle",
        "helmet",
        "tyre",
        "tire",
        "dashcam",
        "car cover",
        "bike",
        "automotive",
    ]

    # ------------------------------------------------------------
    # Electronics
    # ------------------------------------------------------------

    electronics_keywords = [
        "smartphone",
        "mobile phone",
        "mobile",
        "iphone",
        "tablet",
        "laptop",
        "computer",
        "monitor",
        "keyboard",
        "mouse",
        "headphone",
        "headphones",
        "earphone",
        "earphones",
        "earbud",
        "earbuds",
        "neckband",
        "speaker",
        "soundbar",
        "television",
        "tv",
        "smartwatch",
        "camera",
        "printer",
        "router",
        "power bank",
        "charger",
        "cable",
        "airpods",
        "bluetooth",
        "ssd",
        "hard disk",
        "pendrive",
        "refrigerator",
        "fridge",
        "washing machine",
        "air conditioner",
        "microwave",
        "electronics",
    ]

    # ------------------------------------------------------------
    # Priority order
    # ------------------------------------------------------------

    category_groups = [
        ("Beauty", beauty_keywords),
        ("Fashion", fashion_keywords),
        ("Grocery", grocery_keywords),
        ("Home & Kitchen", home_keywords),
        ("Kids", kids_keywords),
        ("Sports", sports_keywords),
        ("Automotive", automotive_keywords),
        ("Electronics", electronics_keywords),
    ]

    for category, keywords in category_groups:

        for keyword in keywords:

            if keyword in text_lower:
                return category

    return "Other"


# ============================================================
# FINANCE / NON-PRODUCT FILTER
# ============================================================

def is_non_product_offer(text):
    """
    Identify finance/banking/loan and other non-product promotions.
    """

    if not text:
        return False

    text_lower = text.lower()

    blocked_keywords = [

        # Credit cards
        "credit card",
        "creditcard",
        "credit card offer",
        "credit card offers",
        "apply for credit card",
        "apply now for credit card",
        "new credit card",

        # Debit / bank
        "debit card",
        "bank offer",
        "bank offers",
        "banking offer",
        "banking offers",
        "bank account",
        "savings account",
        "current account",

        # Loans
        "loan",
        "personal loan",
        "home loan",
        "car loan",
        "bike loan",
        "business loan",
        "instant loan",
        "cash loan",
        "loan offer",
        "loan offers",

        # EMI / credit
        "emi card",
        "credit limit",
        "credit line",
        "buy now pay later",
        "bnpl",
        "pay later",

        # Insurance
        "insurance",
        "health insurance",
        "life insurance",
        "car insurance",
        "bike insurance",

        # Investment / trading
        "mutual fund",
        "investment plan",
        "investment offer",
        "invest now",
        "open demat",
        "demat account",
        "trading account",
        "stock trading",
        "trading app",
        "share market",
        "stock market",
    ]

    for keyword in blocked_keywords:

        if keyword in text_lower:
            return True

    return False


# ============================================================
# TITLE CLEANING
# ============================================================

def clean_title(text):
    """
    Create a cleaner product title from Telegram message.
    """

    if not text:
        return "Deal"

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    if not lines:
        return "Deal"

    # Remove obvious URL-only lines
    filtered_lines = []

    for line in lines:

        if re.fullmatch(r'https?://\S+', line):
            continue

        filtered_lines.append(line)

    if not filtered_lines:
        return "Deal"

    title = filtered_lines[0]

    # Remove common Telegram decorative symbols
    title = re.sub(
        r'^[🔥⭐🌟✨⚡🚨🎉🎁💥🛍️🛒]+\s*',
        '',
        title
    )

    # Remove leading bullets
    title = re.sub(
        r'^[•\-–—]+\s*',
        '',
        title
    )

    # Remove excessive spaces
    title = re.sub(
        r'\s+',
        ' ',
        title
    ).strip()

    # If first line is only a number/price, try next line
    if re.fullmatch(r'[₹\d,\s]+', title):

        if len(filtered_lines) > 1:
            title = filtered_lines[1].strip()

    # Prevent absurdly long titles
    if len(title) > 150:
        title = title[:147].rstrip() + "..."

    return title


# ============================================================
# DESCRIPTION
# ============================================================

def create_description(text):
    """
    Create a short description while keeping useful deal information.
    """

    if not text:
        return ""

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    useful_lines = []

    for line in lines:

        # Skip URL-only lines
        if re.fullmatch(r'https?://\S+', line):
            continue

        # Skip title line
        if not useful_lines:
            useful_lines.append(line)
            continue

        useful_lines.append(line)

    description = " ".join(useful_lines)

    description = re.sub(
        r'\s+',
        ' ',
        description
    ).strip()

    if len(description) > 300:
        description = description[:297].rstrip() + "..."

    return description


# ============================================================
# MAIN PARSER
# ============================================================

def parse_offer(text):

    if not text:
        return {
            "title": "Deal",
            "store": "Other",
            "discount": None,
            "category": "Other",
            "description": "",
            "links": [],
            "price": None,
            "brand": None,
            "is_non_product": False,
        }

    links = extract_links(text)
    discount = extract_discount(text)
    price = extract_price(text)

    # Store is detected from both Telegram text
    # and all URLs contained inside the message.
    store = detect_store(text)

    brand = detect_brand(text)
    category = detect_category(text)
    title = clean_title(text)
    description = create_description(text)

    return {
        "title": title,
        "store": store,
        "discount": discount,
        "category": category,
        "description": description,
        "links": links,
        "price": price,
        "brand": brand,
        "is_non_product": is_non_product_offer(text),
    }