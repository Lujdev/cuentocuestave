from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class MatchCandidate:
    canonical_product_id: str
    display_name: str
    brand: str | None
    canonical_unit: str
    canonical_pack_size: Decimal
    cosine_similarity: float


@dataclass
class MatchDecision:
    canonical_product_id: str | None  # None = no match
    confidence: float  # 0.0-1.0
    reasoning: str


class LLMProvider(ABC):
    @abstractmethod
    async def match_listing(
        self,
        raw_name: str,
        raw_brand: str | None,
        raw_unit: str | None,
        candidates: list[MatchCandidate],
    ) -> MatchDecision:
        ...
