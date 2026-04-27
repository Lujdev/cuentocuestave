from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalise_pg_url(url: str) -> str:
    """Ensure psycopg v3 driver scheme and SSL for Neon endpoints."""
    # Fix explicit psycopg2
    url = url.replace("postgresql+psycopg2://", "postgresql+psycopg://")
    url = url.replace("postgres+psycopg2://", "postgresql+psycopg://")
    # Bare scheme with no explicit driver → SQLAlchemy defaults to psycopg2
    for bare in ("postgresql://", "postgres://"):
        if url.startswith(bare):
            url = "postgresql+psycopg://" + url[len(bare) :]
            break
    # Neon endpoints require SSL + channel binding
    if "neon.tech" in url:
        if "sslmode=" not in url:
            sep = "&" if "?" in url else "?"
            url += f"{sep}sslmode=require"
        if "channel_binding=" not in url:
            url += "&channel_binding=require"
        # Strip pooler suffix — Neon project has pooler_enabled=false
        url = url.replace("-pooler.c-", ".c-")
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str
    database_url_sync: str

    @field_validator("database_url", "database_url_sync", mode="before")
    @classmethod
    def normalise_db_url(cls, v: str) -> str:
        return _normalise_pg_url(v)

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # LLM
    openrouter_api_key: str
    llm_model: str = "deepseek/deepseek-v4-flash"
    llm_fallback_model: str = "anthropic/claude-haiku-4.5"
    llm_daily_budget_usd: float = 1.0

    # Auth (Neon Auth / better-auth)
    neon_auth_url: str  # e.g. https://ep-xxx.neonauth.region.aws.neon.tech/dbname/auth
    admin_allowed_email: str

    # App
    environment: str = "development"
    log_level: str = "INFO"
    secret_key: str
    sentry_dsn: str = ""

    # CORS
    cors_origins: list[str] = ["http://localhost:4321", "http://localhost:5173"]
