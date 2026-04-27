"""Plaza's supermarket scraper — Scrapling DynamicFetcher (Playwright-based)."""

from decimal import Decimal, InvalidOperation

import structlog

from cuantocuestave_domain.ports.scraper import RawListing
from cuantocuestave_infra.scrapers.base import BaseScrapler

logger = structlog.get_logger(__name__)

BASE_URL = "https://www.plazas.com.ve"

# Category URLs to crawl. Each entry is (category_slug, full_url).
# TODO: verify selectors against live Plaza's site — actual category paths must
# be confirmed against a live browser session; the slugs below are placeholders
# based on the supermarket's known catalogue structure.
CATEGORY_URLS: list[tuple[str, str]] = [
    ("cereales", f"{BASE_URL}/catalogsearch/result/?q=harina"),
    ("aceites", f"{BASE_URL}/catalogsearch/result/?q=aceite"),
    ("lacteos", f"{BASE_URL}/catalogsearch/result/?q=leche"),
    ("carnes", f"{BASE_URL}/catalogsearch/result/?q=mortadela"),
    ("azucares", f"{BASE_URL}/catalogsearch/result/?q=azucar"),
    ("higiene", f"{BASE_URL}/catalogsearch/result/?q=jabon"),
    ("limpieza", f"{BASE_URL}/catalogsearch/result/?q=detergente"),
    ("bebidas", f"{BASE_URL}/catalogsearch/result/?q=cafe"),
]


def _parse_price(raw: str) -> Decimal | None:
    """Normalise a price string like '$4.99' or '4,99' to a Decimal."""
    cleaned = raw.strip().replace("$", "").replace(",", ".").replace("\xa0", "")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


class PlazasScraper(BaseScrapler):
    """Scraper for plazas.com.ve using Scrapling DynamicFetcher (Playwright)."""

    supermarket_slug = "plazas"

    async def _fetch_listings(self) -> list[RawListing]:
        # Import here so Scrapling/Playwright is only required at runtime.
        from scrapling.fetchers import PlayWrightFetcher  # type: ignore[import-untyped]

        listings: list[RawListing] = []

        for category_slug, url in CATEGORY_URLS:
            log = logger.bind(supermarket=self.supermarket_slug, category=category_slug, url=url)
            log.info("category_fetch_start")

            try:
                # TODO: verify selectors against live Plaza's site —
                # DynamicFetcher waits for JS-rendered content before returning.
                fetcher = PlayWrightFetcher(auto_match=False)
                page = await fetcher.async_fetch(
                    url,
                    wait_selector=".product-card",  # TODO: verify selector against live Plaza's site
                    timeout=30_000,
                )
            except Exception as exc:
                log.error("category_fetch_error", error=str(exc))
                continue

            # TODO: verify selectors against live Plaza's site
            # Common Magento/custom e-commerce patterns used below as best guesses.
            product_cards = page.css(".product-card")  # TODO: verify selector
            log.info("cards_found", count=len(product_cards))

            for card in product_cards:
                try:
                    # TODO: verify selector against live Plaza's site
                    name_el = card.css_first(".product-name") or card.css_first(".product-title")
                    price_el = card.css_first(".price") or card.css_first(".product-price")
                    sku_el = card.css_first(".product-sku") or card.css_first("[data-sku]")
                    img_el = card.css_first("img")
                    link_el = card.css_first("a")

                    if name_el is None or price_el is None:
                        log.debug("card_missing_fields", html=card.html[:200])
                        continue

                    raw_name: str = name_el.text.strip()
                    price_str: str = price_el.text.strip()
                    price = _parse_price(price_str)

                    if price is None or price <= 0:
                        log.warning("invalid_price", raw=price_str, name=raw_name)
                        continue

                    # External ID: prefer SKU, fall back to slugified name
                    if sku_el is not None:
                        external_id = (
                            sku_el.attrib.get("data-sku") or sku_el.text.strip() or raw_name
                        )
                    else:
                        external_id = raw_name

                    image_url: str | None = img_el.attrib.get("src") if img_el else None
                    product_url: str | None = None
                    if link_el is not None:
                        href = link_el.attrib.get("href", "")
                        product_url = href if href.startswith("http") else f"{BASE_URL}{href}"

                    listings.append(
                        RawListing(
                            external_id=external_id,
                            raw_name=raw_name,
                            raw_brand=None,  # TODO: extract brand if available
                            raw_unit=None,  # TODO: extract unit from name/badge
                            raw_category=category_slug,
                            price_local=price,
                            currency="USD",  # Plaza's prices are in USD
                            available=True,
                            image_url=image_url,
                            product_url=product_url,
                        )
                    )
                except Exception as exc:
                    log.error("card_parse_error", error=str(exc))
                    continue

        logger.info(
            "plazas_scrape_complete",
            total_listings=len(listings),
            categories=len(CATEGORY_URLS),
        )
        return listings
