import { useEffect, useState } from "react";
import "./App.css";

type Offer = {
  id: number;
  telegram_message_id: number;
  title: string;
  store: string;
  discount: string | null;
  category: string;
  description: string;
  links: string;
  image_url: string | null;
  fallback_image_url: string | null;
  message_date: string;
};

const filters = [
  "All Deals",
  "Amazon",
  "Myntra",
  "AJIO",
  "Flipkart",
  "Fashion",
  "Beauty",
  "Electronics",
];

function App() {
  const [offers, setOffers] = useState<Offer[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [activeFilter, setActiveFilter] = useState("All Deals");

  const fetchOffers = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/offers"
      );

      const data = await response.json();

      setOffers(data.offers);
      setLoading(false);
    } catch (error) {
      console.error("Failed to load offers:", error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOffers();

    const interval = setInterval(() => {
      fetchOffers();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const newDeals = offers.filter((offer) => {
    const offerTime = new Date(
      offer.message_date
    ).getTime();

    return Date.now() - offerTime <= 60 * 1000;
  });

  const filteredOffers = offers.filter((offer) => {
    const searchText = search.toLowerCase().trim();

    const matchesSearch =
      !searchText ||
      offer.title.toLowerCase().includes(searchText) ||
      offer.store.toLowerCase().includes(searchText) ||
      offer.category.toLowerCase().includes(searchText) ||
      offer.description.toLowerCase().includes(searchText);

    const matchesFilter =
      activeFilter === "All Deals" ||
      offer.store.toLowerCase() ===
        activeFilter.toLowerCase() ||
      offer.category.toLowerCase() ===
        activeFilter.toLowerCase();

    return matchesSearch && matchesFilter;
  });

  const selectFilter = (filter: string) => {
    setActiveFilter(filter);
    setSearch("");

    setTimeout(() => {
      document
        .getElementById("deals")
        ?.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
    }, 50);
  };

  return (
    <div className="app">

      {/* HEADER */}
      <header className="header">

        <div className="logo">
          <span className="logo-mark">DZ</span>
          <span>DealZone</span>
        </div>

        <nav className="main-nav">
          <a
            href="#"
            onClick={() => {
              setActiveFilter("All Deals");
              setSearch("");
            }}
          >
            Home
          </a>

          <a
            href="#deals"
            onClick={() => selectFilter("Amazon")}
          >
            Amazon
          </a>

          <a
            href="#deals"
            onClick={() => selectFilter("Myntra")}
          >
            Myntra
          </a>

          <a
            href="#deals"
            onClick={() => selectFilter("AJIO")}
          >
            AJIO
          </a>

          <a
            href="#deals"
            onClick={() => selectFilter("Flipkart")}
          >
            Flipkart
          </a>

          <a
            href="#deals"
            onClick={() => selectFilter("Electronics")}
          >
            Electronics
          </a>
        </nav>

        <div className="search">
          <span className="search-icon">⌕</span>

          <input
            type="text"
            placeholder="Search deals..."
            value={search}
            onChange={(event) =>
              setSearch(event.target.value)
            }
          />
        </div>

      </header>


      {/* HERO / COVER */}
      <section className="hero">

        <div className="hero-content">

          <span className="hero-eyebrow">
            SMART SHOPPING
          </span>

          <h1>
            Smart Deals.
            <br />
            Better Prices.
          </h1>

          <p>
            Discover the latest deals, discounts and
            offers from popular stores — all in one place.
          </p>

          <div className="hero-actions">

            <button
              className="primary-button"
              onClick={() => {
                setActiveFilter("All Deals");
                setSearch("");

                document
                  .getElementById("deals")
                  ?.scrollIntoView({
                    behavior: "smooth",
                  });
              }}
            >
              Explore Deals
              <span>→</span>
            </button>

            <button
              className="secondary-button"
              onClick={() =>
                document
                  .getElementById("stores")
                  ?.scrollIntoView({
                    behavior: "smooth",
                  })
              }
            >
              Browse Stores
            </button>

          </div>

          <div className="hero-stats">

            <div>
              <strong>{offers.length}+</strong>
              <span>Active Deals</span>
            </div>

            <div>
              <strong>14+</strong>
              <span>Store Categories</span>
            </div>

            <div>
              <strong>Daily</strong>
              <span>Fresh Updates</span>
            </div>

          </div>

        </div>

        <div className="hero-visual">

          <div className="hero-orbit orbit-one"></div>
          <div className="hero-orbit orbit-two"></div>

          <div className="deal-showcase">

            <span className="showcase-label">
              DEAL OF THE DAY
            </span>

            <strong>
              Discover
              <br />
              More. Save
              <br />
              More.
            </strong>

            <span className="showcase-arrow">
              →
            </span>

          </div>

        </div>

      </section>


      {/* STORE / CATEGORY FILTERS */}
      <section
        className="categories-section"
        id="stores"
      >

        <div className="section-heading compact-heading">

          <div>
            <span className="section-eyebrow">
              SHOP BY
            </span>

            <h2>
              Popular Stores & Categories
            </h2>
          </div>

        </div>

        <div className="categories">

          {filters.map((filter) => (
            <button
              key={filter}
              className={
                activeFilter === filter
                  ? "active"
                  : ""
              }
              onClick={() =>
                selectFilter(filter)
              }
            >
              {filter}
            </button>
          ))}

        </div>

      </section>


      {/* NEW DEALS */}
      {newDeals.length > 0 && (
        <section className="container new-deals-section">

          <div className="section-heading">

            <div>
              <span className="section-eyebrow">
                JUST ARRIVED
              </span>

              <h2>
                New Deals
              </h2>
            </div>

            <span className="deal-count">
              {newDeals.length} new
            </span>

          </div>

          <div className="offers-grid">

            {newDeals.slice(0, 8).map((offer) => (
              <OfferCard
                key={`new-${offer.id}`}
                offer={offer}
                isNew
              />
            ))}

          </div>

        </section>
      )}


      {/* MAIN DEALS */}
      <main
        className="container deals-section"
        id="deals"
      >

        <div className="section-heading">

          <div>

            <span className="section-eyebrow">
              LATEST OFFERS
            </span>

            <h2>
              {activeFilter === "All Deals"
                ? "Latest Deals"
                : `${activeFilter} Deals`}
            </h2>

          </div>

          <span className="deal-count">
            {filteredOffers.length} deals
          </span>

        </div>


        {/* SEARCH STATUS */}
        {search && (
          <div className="search-status">
            Results for
            <strong> "{search}"</strong>
          </div>
        )}


        {/* LOADING */}
        {loading ? (

          <div className="loading">
            <div className="loading-spinner"></div>
            <p>Loading latest deals...</p>
          </div>

        ) : filteredOffers.length === 0 ? (

          <div className="empty-state">

            <h3>
              No deals found
            </h3>

            <p>
              Try another search or category.
            </p>

            <button
              onClick={() => {
                setSearch("");
                setActiveFilter("All Deals");
              }}
            >
              View All Deals
            </button>

          </div>

        ) : (

          <div className="offers-grid">

            {filteredOffers.map((offer) => (
              <OfferCard
                key={offer.id}
                offer={offer}
              />
            ))}

          </div>

        )}

      </main>


      {/* AD PLACEHOLDER */}
      <section className="ad-slot">
        <span>ADVERTISEMENT</span>
      </section>


      {/* ABOUT */}
      <section className="about-section">

        <div className="about-content">

          <span className="section-eyebrow">
            ABOUT DEALZONE
          </span>

          <h2>
            Find more.
            <br />
            Spend less.
          </h2>

          <p>
            DealZone brings together useful deals,
            discounts and offers from popular online
            stores so you can discover better prices
            without searching everywhere.
          </p>

        </div>

      </section>


      {/* FOOTER */}
      <footer className="footer">

        <div className="footer-brand">

          <div className="logo">
            <span className="logo-mark">DZ</span>
            <span>DealZone</span>
          </div>

          <p>
            Smart deals. Better prices.
          </p>

        </div>

        <div className="footer-links">

          <a href="#deals">
            Deals
          </a>

          <a href="#stores">
            Stores
          </a>

          <a href="#">
            About
          </a>

          <a href="#">
            Contact
          </a>

          <a href="#">
            Privacy Policy
          </a>

          <a href="#">
            Terms
          </a>

        </div>

        <div className="footer-bottom">

          <span>
            © 2026 DealZone
          </span>

          <span>
            All rights reserved.
          </span>

        </div>

      </footer>

    </div>
  );
}


/* OFFER CARD */

function OfferCard({
  offer,
  isNew = false,
}: {
  offer: Offer;
  isNew?: boolean;
}) {

  return (
    <article
      className={
        isNew
          ? "offer-card new-deal-card"
          : "offer-card"
      }
    >

      <div className="offer-image">

        {isNew && (
          <span className="new-badge">
            NEW
          </span>
        )}

        <span className="discount-badge">
          {offer.discount || "DEAL"}
        </span>

        {/* Store logo only.
            Telegram product images are intentionally ignored. */}
        {offer.fallback_image_url ? (

          <img
            src={`http://127.0.0.1:8000${offer.fallback_image_url}`}
            alt={offer.store}
            className="offer-product-image store-logo"
          />

        ) : (

          <div className="placeholder-image">
            <span>DealZone</span>
          </div>

        )}

      </div>


      <div className="offer-content">

        <div className="offer-meta">

        <span>
          {offer.store}
        </span>

        {offer.category &&
          offer.category.toLowerCase() !== "other" && (
            <span>
              {offer.category}
            </span>
          )}

      </div>


        <h3>
          {cleanTitle(offer.title)}
        </h3>


        <p>
          {cleanDescription(
            offer.description
          )}
        </p>


        <div className="offer-footer">

          <small>
            {formatRelativeTime(
              offer.message_date
            )}
          </small>

          <a
            href={getFirstLink(
              offer.links
            )}
            target="_blank"
            rel="noopener noreferrer"
          >
            View Deal
            <span>→</span>
          </a>

        </div>

      </div>

    </article>
  );
}


/* GET FIRST DEAL LINK */

function getFirstLink(links: string) {

  try {

    const parsed = JSON.parse(links);

    if (
      Array.isArray(parsed) &&
      parsed.length > 0
    ) {
      return parsed[0];
    }

  } catch {
    // Ignore invalid JSON
  }

  return "#";
}


/* CLEAN TITLE */
function removeEmojis(text: string) {
  return [...text]
    .filter((char) => {
      const code = char.codePointAt(0) || 0;

      return !(
        (code >= 0x1f000 && code <= 0x1faff) ||
        (code >= 0x2600 && code <= 0x27bf) ||
        code === 0xfe0f ||
        code === 0x200d
      );
    })
    .join("");
}


/* CLEAN TITLE */

function cleanTitle(title: string) {
  return removeEmojis(title)
    .replace(/\*\*/g, "")
    .replace(/__/g, "")
    .replace(/`/g, "")
    .replace(/\s+/g, " ")
    .trim();
}


/* CLEAN DESCRIPTION */

function cleanDescription(description: string) {
  return removeEmojis(description)
    .replace(/\*\*/g, "")
    .replace(/__/g, "")
    .replace(/`/g, "")
    .replace(/https?:\/\/\S+/gi, "")
    .replace(/\n+/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 150);
}
/* RELATIVE TIME */

function formatRelativeTime(
  dateString: string
) {

  const offerTime =
    new Date(dateString).getTime();

  const diffSeconds =
    Math.floor(
      (Date.now() - offerTime) / 1000
    );

  if (diffSeconds < 60) {
    return "Just now";
  }

  const diffMinutes =
    Math.floor(diffSeconds / 60);

  if (diffMinutes < 60) {
    return `${diffMinutes} min ago`;
  }

  const diffHours =
    Math.floor(diffMinutes / 60);

  if (diffHours < 24) {
    return `${diffHours} hr ago`;
  }

  const diffDays =
    Math.floor(diffHours / 24);

  return `${diffDays} days ago`;
}


export default App;