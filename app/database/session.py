from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass


SQLITE_URL = "sqlite+aiosqlite:///./data/bot.db"


def create_engine_and_session():
    engine = create_async_engine(
        SQLITE_URL,
        echo=False,
        pool_pre_ping=True,
    )

    session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    return engine, session_maker
