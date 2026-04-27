"""Unit tests for fetch_monitor_dolar_rate using httpx mocking."""
from datetime import UTC, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from cuantocuestave_infra.exchange.monitor_dolar import fetch_monitor_dolar_rate
from cuantocuestave_infra.exchange.types import ExchangeRateFetchError


def _mock_response(payload: dict, status_code: int = 200) -> MagicMock:
    mock = MagicMock(spec=httpx.Response)
    mock.status_code = status_code
    mock.json.return_value = payload
    mock.raise_for_status = MagicMock()
    if status_code >= 400:
        mock.raise_for_status.side_effect = httpx.HTTPStatusError(
            message=f"HTTP {status_code}",
            request=MagicMock(),
            response=mock,
        )
    return mock


@pytest.mark.asyncio
async def test_fetch_monitor_dolar_rate_success() -> None:
    payload = {
        "nombre": "Paralelo",
        "promedio": 95.12,
        "promedio_compra": 95.00,
        "promedio_venta": 95.25,
        "fecha_actualizacion": "2026-04-26T18:00:00.000Z",
    }
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=_mock_response(payload))

    with patch("cuantocuestave_infra.exchange.monitor_dolar.httpx.AsyncClient", return_value=mock_client):
        reading = await fetch_monitor_dolar_rate()

    assert reading.source == "monitor_dolar_ve"
    assert reading.rate_ves_per_usd == Decimal("95.12")
    assert reading.raw_payload["nombre"] == "Paralelo"


@pytest.mark.asyncio
async def test_fetch_monitor_dolar_rate_missing_promedio() -> None:
    payload = {"nombre": "Paralelo"}  # no 'promedio' key
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=_mock_response(payload))

    with patch("cuantocuestave_infra.exchange.monitor_dolar.httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(ExchangeRateFetchError, match="'promedio' field missing"):
            await fetch_monitor_dolar_rate()


@pytest.mark.asyncio
async def test_fetch_monitor_dolar_rate_zero_rate() -> None:
    payload = {"promedio": 0}
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(return_value=_mock_response(payload))

    with patch("cuantocuestave_infra.exchange.monitor_dolar.httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(ExchangeRateFetchError, match="Invalid rate"):
            await fetch_monitor_dolar_rate()


@pytest.mark.asyncio
async def test_fetch_monitor_dolar_rate_http_error() -> None:
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)
    mock_client.get = AsyncMock(side_effect=httpx.ConnectError("refused"))

    with patch("cuantocuestave_infra.exchange.monitor_dolar.httpx.AsyncClient", return_value=mock_client):
        with pytest.raises(ExchangeRateFetchError, match="HTTP error"):
            # tenacity retries 3× — patch stop so the test is fast
            with patch("cuantocuestave_infra.exchange.monitor_dolar.fetch_monitor_dolar_rate.retry.stop"):
                await fetch_monitor_dolar_rate()
