from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str  # "USD" | "VES"

    def to_usd(self, rate_ves_per_usd: Decimal) -> "Money":
        if self.currency == "USD":
            return self
        return Money(amount=self.amount / rate_ves_per_usd, currency="USD")

    def to_ves(self, rate_ves_per_usd: Decimal) -> "Money":
        if self.currency == "VES":
            return self
        return Money(amount=self.amount * rate_ves_per_usd, currency="VES")

    def __str__(self) -> str:
        symbol = "$" if self.currency == "USD" else "Bs."
        return f"{symbol}{self.amount:.2f}"
