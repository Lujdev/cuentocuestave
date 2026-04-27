from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    database_url: str
    database_url_sync: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # LLM
    openrouter_api_key: str
    llm_model: str = "deepseek/deepseek-v4-flash"
    llm_fallback_model: str = "anthropic/claude-haiku-4.5"
    llm_daily_budget_usd: float = 1.0

    # Auth
    stack_auth_project_id: str = ""
    stack_auth_secret_server_key: str = ""
    admin_allowed_email: str

    # App
    environment: str = "development"
    log_level: str = "INFO"
    secret_key: str
    sentry_dsn: str = ""

    # CORS
    cors_origins: list[str] = ["http://localhost:4321", "http://localhost:5173"]
