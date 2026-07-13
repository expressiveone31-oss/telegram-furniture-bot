from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

class Base(DeclarativeBase):
    pass


def _normalize_database_url(url: str) -> str:
    """
    Railway отдаёт PostgreSQL URL в формате postgresql:// или postgres://.
    Для async SQLAlchemy нужен postgresql+asyncpg://.
    """
    url = url.strip()
    if not url:
        raise ValueError(
            "DATABASE_URL задан пустым. Проверьте переменную DATABASE_URL "
            "в сервисе telegram-furniture-bot на Railway."
        )
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://") and "+asyncpg" not in url:
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


def create_engine_and_session():
    database_url = _normalize_database_url(settings.database_url)

    engine = create_async_engine(
        database_url,
        echo=False,
        pool_pre_ping=True,
    )

    session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return engine, session_maker
