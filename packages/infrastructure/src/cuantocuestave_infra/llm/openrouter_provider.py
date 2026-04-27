"""OpenRouter LLM provider implementing LLMProvider port."""
import hashlib
import json
import structlog
from openai import AsyncOpenAI

from cuantocuestave_domain.ports.llm import LLMProvider, MatchCandidate, MatchDecision
from cuantocuestave_infra.settings import Settings

logger = structlog.get_logger(__name__)

MATCH_SYSTEM_PROMPT = """You are a product matching expert for Venezuelan supermarkets.
Given a product listing and a list of canonical product candidates, decide which candidate best matches the listing.
Respond ONLY with valid JSON matching the schema provided."""

MATCH_SCHEMA = {
    "type": "object",
    "properties": {
        "canonical_product_id": {"type": ["string", "null"]},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "reasoning": {"type": "string"},
    },
    "required": ["canonical_product_id", "confidence", "reasoning"],
    "additionalProperties": False,
}


class OpenRouterProvider(LLMProvider):
    def __init__(self, settings: Settings, redis_client=None) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.openrouter_api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        self._model = settings.llm_model
        self._fallback_model = settings.llm_fallback_model
        self._budget_usd = settings.llm_daily_budget_usd
        self._redis = redis_client

    async def match_listing(
        self,
        raw_name: str,
        raw_brand: str | None,
        raw_unit: str | None,
        candidates: list[MatchCandidate],
    ) -> MatchDecision:
        prompt = self._build_prompt(raw_name, raw_brand, raw_unit, candidates)
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()

        # Check Redis cache first
        if self._redis:
            cached = await self._redis.get(f"llm:match:{prompt_hash}")
            if cached:
                data = json.loads(cached)
                return MatchDecision(**data)

        decision = await self._call_llm(prompt, self._model)

        # Fallback if confidence too low
        if decision.confidence < 0.7:
            logger.info("llm_fallback_triggered", confidence=decision.confidence)
            decision = await self._call_llm(prompt, self._fallback_model)

        # Cache result for 90 days
        if self._redis:
            await self._redis.setex(
                f"llm:match:{prompt_hash}",
                90 * 24 * 3600,
                json.dumps({"canonical_product_id": decision.canonical_product_id,
                            "confidence": decision.confidence,
                            "reasoning": decision.reasoning}),
            )

        return decision

    def _build_prompt(
        self,
        raw_name: str,
        raw_brand: str | None,
        raw_unit: str | None,
        candidates: list[MatchCandidate],
    ) -> str:
        listing_desc = f"Name: {raw_name}"
        if raw_brand:
            listing_desc += f", Brand: {raw_brand}"
        if raw_unit:
            listing_desc += f", Unit: {raw_unit}"

        candidates_json = json.dumps(
            [
                {
                    "id": c.canonical_product_id,
                    "name": c.display_name,
                    "brand": c.brand,
                    "unit": c.canonical_unit,
                    "pack_size": str(c.canonical_pack_size),
                    "similarity": round(c.cosine_similarity, 4),
                }
                for c in candidates
            ],
            ensure_ascii=False,
            indent=2,
        )

        return f"""Listing: {listing_desc}

Candidates (sorted by cosine similarity):
{candidates_json}

Pick the best matching candidate or return null if none match. Return JSON only."""

    async def _call_llm(self, prompt: str, model: str) -> MatchDecision:
        response = await self._client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": MATCH_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_schema", "json_schema": {"name": "match", "schema": MATCH_SCHEMA}},
            temperature=0.0,
            max_tokens=256,
        )
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        return MatchDecision(
            canonical_product_id=data.get("canonical_product_id"),
            confidence=float(data.get("confidence", 0.0)),
            reasoning=data.get("reasoning", ""),
        )
