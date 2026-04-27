"""Unit tests for fetch_bcv_rate and _parse_bcv_html."""
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from cuantocuestave_infra.exchange.bcv import _parse_bcv_html, fetch_bcv_rate
from cuantocuestave_infra.exchange.types import ExchangeRateFetchError

# Minimal BCV-style HTML fragments for parser unit tests
_HTML_WITH_DIV = """
<html><body>
  <div id="dolar">
    <strong>36,50</strong>
    <span>Dólar EEUU</span>
  </div>
</body></html>
"""

_HTML_WITH_TABLE = """
<html><body>
  <table>
    <tr><th>Divisa</th><th>Tasa</th></tr>
    <tr><td>Dólar</td><td>36.50</td></tr>
    <tr><td>Euro</td><td>38.12</td></tr>
  </table>
</body></html>
"""

_HTML_NO_RATE = """
<html><body><p>Sin datos disponibles</p></body></html>
"""


def test_parse_bcv_html_div_strategy() -> None:
    rate = _parse_bcv_html(_HTML_WITH_DIV)
    assert rate == Decimal("36.50")


def test_parse_bcv_html_table_fallback() -> None:
    # Patch div strategy to not find anything, forcing table strategy
    html = _HTML_WITH_TABLE
    rate = _parse_bcv_html(html)
    assert rate == Decimal("36.50")


def test_parse_bcv_html_no_rate_raises() -> None:
    with pytest.raises(ExchangeRateFetchError, match="Could not locate"):
        _parse_bcv_html(_HTML_NO_RATE)


def _mock_http_response(html: str, status_code: int = 200) -> MagicMock:
    mock = MagicMock(spec=httpx.Response)
    mock.status_code = status_code
    mock.text = html
    mock.raise_for_status = MagicMock()
    if status_code >= 400:
        mock.raise_for_status.side_effect = httpx.HTTPStatusError(
            message=f"HTTP {status_code}",
            request=MagicMock(),
            response=mock,
        )
    return mock


@pytest.mark.asyncio
async def test_fetch_bcv_rate_success() -> None:
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=_mock_http_response(_HTML_WITH_DIV))

    with patch("cuantocuestave_infra.exchange.bcv.httpx.AsyncClient", return_value=mock_client):
        reading = await fetch_bcv_rate()

    assert reading.source == "bcv"
    assert reading.rate_ves_per_usd == Decimal("36.50")


@pytest.mark.asyncio
async def test_fetch_bcv_rate_http_error_raises() -> None:
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))

    with patch("cuantocuestave_infra.exchange.bcv.httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(ExchangeRateFetchError):
            with patch("cuantocuestave_infra.exchange.bcv.fetch_bcv_rate.retry.stop"):
                await fetch_bcv_rate()
