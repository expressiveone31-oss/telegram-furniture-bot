from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass


DATABASE_URL = "sqlite+aiosqlite:///./data/bot.db"


def _normalize_database_url(url: str) -> str:
    """Normalize a PostgreSQL URL without changing the active SQLite backend."""
    url = url.strip()
    if not url:
        raise ValueError("DATABASE_URL задан пустым")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def create_engine_and_session():
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return engine, session_maker
