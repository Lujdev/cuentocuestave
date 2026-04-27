from dataclasses import dataclass
from uuid import UUID

from cuantocuestave_domain.ports.embedding import EmbeddingProvider
from cuantocuestave_domain.ports.llm import LLMProvider, MatchCandidate
from cuantocuestave_domain.ports.repositories import ProductListingRepository


@dataclass
class MatchListingUseCase:
    listing_repo: ProductListingRepository
    embedding_provider: EmbeddingProvider
    llm_provider: LLMProvider

    AUTO_MATCH_THRESHOLD = 0.92
    LLM_RANGE_LOW = 0.55
    LLM_RANGE_HIGH = 0.92
    LLM_FALLBACK_THRESHOLD = 0.70

    async def execute(self, listing_id: UUID) -> None:
        # 1. Compute embedding
        # 2. Find top-5 candidates by cosine sim via pgvector
        # 3. Apply threshold logic
        # Full implementation in Fase 2
        pass
