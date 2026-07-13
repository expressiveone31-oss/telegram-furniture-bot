from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import create_engine_and_session

_engine = None
_session_maker = None


def _get_database():
    global _engine, _session_maker
    if _engine is None or _session_maker is None:
        _engine, _session_maker = create_engine_and_session()
    return _engine, _session_maker


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    _, session_maker = _get_database()
    async with session_maker() as session:
        yield session


async def init_db():
    from app.database.session import Base
    from app.database.models import Order, Question

    engine, _ = _get_database()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
