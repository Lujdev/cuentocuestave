"""Sentence-transformers embedding provider — singleton model loaded once per worker process."""
import structlog

from cuantocuestave_domain.ports.embedding import EmbeddingProvider

logger = structlog.get_logger(__name__)
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

_model = None


def _get_model():  # type: ignore[no-untyped-def]
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("loading_embedding_model", model=MODEL_NAME)
        _model = SentenceTransformer(MODEL_NAME)
        logger.info("embedding_model_loaded")
    return _model


class SentenceTransformersProvider(EmbeddingProvider):
    async def embed(self, text: str) -> list[float]:
        model = _get_model()
        return model.encode(text, normalize_embeddings=True).tolist()

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        model = _get_model()
        return model.encode(texts, normalize_embeddings=True, batch_size=64).tolist()
