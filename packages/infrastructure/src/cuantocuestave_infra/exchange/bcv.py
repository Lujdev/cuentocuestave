"""BCV (Banco Central de Venezuela) exchange rate fetcher."""

from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from cuantocuestave_infra.exchange.types import ExchangeRateFetchError, ExchangeRateReading

logger = structlog.get_logger(__name__)

_BCV_URL = "https://www.bcv.org.ve/estadisticas/tipos-de-cambio-del-sistema-bancario"

# Timeout in seconds for HTTP calls
_TIMEOUT = 30.0


def _parse_bcv_html(html: str) -> Decimal:
    """Parse the BCV statistics page and extract the USD/VES rate.

    The BCV page renders a table with exchange rates for each currency.
    # TODO: verify selector against live BCV site — the exact element class
    # names and table structure change occasionally. The approach below is
    # based on common BCV HTML patterns observed historically.
    """
    try:
        # Lazy import — bs4 is a common dependency in httpx-based projects
        from bs4 import BeautifulSoup  # type: ignore[import-untyped]
    except ImportError as exc:
        raise ExchangeRateFetchError(
            "beautifulsoup4 is required for BCV parsing. "
            "Add it to cuantocuestave-infrastructure dependencies."
        ) from exc

    soup = BeautifulSoup(html, "html.parser")

    # Strategy 1: look for a <div id="dolar"> or similar element with the rate.
    # TODO: verify selector against live BCV site
    dolar_div = soup.find("div", {"id": "dolar"})
    if dolar_div:
        strong = dolar_div.find("strong")
        if strong and strong.text.strip():
            raw = strong.text.strip().replace(",", ".")
            try:
                return Decimal(raw)
            except InvalidOperation:
                pass

    # Strategy 2: scan table rows for "Dólar" / "Dolar" keyword.
    # TODO: verify selector against live BCV site
    for row in soup.find_all("tr"):
        cells = row.find_all(["td", "th"])
        if len(cells) >= 2:
            header_text = cells[0].get_text(strip=True).lower()
            if "d" in header_text and ("lar" in header_text or "ólar" in header_text):
                raw = cells[-1].get_text(strip=True).replace(",", ".")
                try:
                    return Decimal(raw)
                except InvalidOperation:
                    continue

    raise ExchangeRateFetchError(
        "Could not locate USD/VES rate in BCV page. "
        "The page structure may have changed — review the selectors."
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=2, max=30),
    reraise=True,
)
async def fetch_bcv_rate() -> ExchangeRateReading:
    """Fetch the current official USD/VES exchange rate from BCV.

    Returns an :class:`ExchangeRateReading` with source="bcv".
    Raises :class:`ExchangeRateFetchError` if the rate cannot be obtained.
    """
    log = logger.bind(source="bcv", url=_BCV_URL)
    log.info("bcv_fetch_start")

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True) as client:
            response = await client.get(
                _BCV_URL,
                headers={
                    # TODO: verify selector against live BCV site — UA may affect response
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "es-VE,es;q=0.9",
                },
            )
            response.raise_for_status()
            html = response.text
    except httpx.HTTPError as exc:
        log.error("bcv_http_error", error=str(exc))
        raise ExchangeRateFetchError(f"HTTP error fetching BCV page: {exc}") from exc

    try:
        rate = _parse_bcv_html(html)
    except ExchangeRateFetchError:
        raise
    except Exception as exc:
        log.error("bcv_parse_error", error=str(exc))
        raise ExchangeRateFetchError(f"Unexpected error parsing BCV page: {exc}") from exc

    reading = ExchangeRateReading(
        source="bcv",
        rate_ves_per_usd=rate,
        observed_at=datetime.now(UTC),
        raw_payload={"url": _BCV_URL, "rate_raw": str(rate)},
    )
    log.info("bcv_fetch_done", rate_ves_per_usd=str(rate))
    return reading
