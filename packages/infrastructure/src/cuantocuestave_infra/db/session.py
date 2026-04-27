from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from cuantocuestave_infra.settings import Settings

_settings = Settings()

engine = create_async_engine(
    _settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
