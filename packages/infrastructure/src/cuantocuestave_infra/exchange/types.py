"""Infrastructure-only DTOs for exchange rate fetching — NOT domain entities."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class ExchangeRateReading:
    """Immutable snapshot of an exchange rate observation from an external source."""

    source: str  # "bcv" | "monitor_dolar_ve"
    rate_ves_per_usd: Decimal
    observed_at: datetime
    raw_payload: dict = field(default_factory=dict)


class ExchangeRateFetchError(Exception):
    """Raised when an exchange rate fetcher cannot obtain a valid reading."""
