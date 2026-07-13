from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import create_engine_and_session

_engine, _session_maker = create_engine_and_session()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with _session_maker() as session:
        yield session


async def init_db():
    from app.database.session import Base
    from app.database.models import Order, Question

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
