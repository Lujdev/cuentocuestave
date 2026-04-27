"""Monitor Dólar Venezuela exchange rate fetcher (paralelo / mercado libre)."""

from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from cuantocuestave_infra.exchange.types import ExchangeRateFetchError, ExchangeRateReading

logger = structlog.get_logger(__name__)

_MONITOR_URL = "https://ve.dolarapi.com/v1/dolares/paralelo"
_TIMEOUT = 15.0


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=2, max=30),
    reraise=True,
)
async def fetch_monitor_dolar_rate() -> ExchangeRateReading:
    """Fetch the parallel (mercado libre) USD/VES exchange rate from dolarapi.com.

    Endpoint: GET https://ve.dolarapi.com/v1/dolares/paralelo
    Response JSON example:
        {
          "nombre": "Paralelo",
          "promedio": 95.12,
          "promedio_compra": 95.00,
          "promedio_venta": 95.25,
          "fecha_actualizacion": "2026-04-26T18:00:00.000Z"
        }

    Returns an :class:`ExchangeRateReading` with source="monitor_dolar_ve".
    Raises :class:`ExchangeRateFetchError` if the rate cannot be obtained.
    """
    log = logger.bind(source="monitor_dolar_ve", url=_MONITOR_URL)
    log.info("monitor_dolar_fetch_start")

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT, follow_redirects=True) as client:
            response = await client.get(
                _MONITOR_URL,
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPStatusError as exc:
        log.error("monitor_dolar_http_status_error", status=exc.response.status_code)
        raise ExchangeRateFetchError(
            f"HTTP {exc.response.status_code} fetching monitor dolar: {exc}"
        ) from exc
    except httpx.HTTPError as exc:
        log.error("monitor_dolar_http_error", error=str(exc))
        raise ExchangeRateFetchError(f"HTTP error fetching monitor dolar: {exc}") from exc
    except Exception as exc:
        log.error("monitor_dolar_unexpected_error", error=str(exc))
        raise ExchangeRateFetchError(f"Unexpected error: {exc}") from exc

    promedio = payload.get("promedio")
    if promedio is None:
        raise ExchangeRateFetchError(
            f"'promedio' field missing from monitor dolar response: {payload}"
        )

    try:
        rate = Decimal(str(promedio))
    except InvalidOperation as exc:
        raise ExchangeRateFetchError(f"Cannot convert 'promedio' to Decimal: {promedio!r}") from exc

    if rate <= 0:
        raise ExchangeRateFetchError(f"Invalid rate from monitor dolar: {rate}")

    reading = ExchangeRateReading(
        source="monitor_dolar_ve",
        rate_ves_per_usd=rate,
        observed_at=datetime.now(UTC),
        raw_payload=payload,
    )
    log.info("monitor_dolar_fetch_done", rate_ves_per_usd=str(rate))
    return reading
