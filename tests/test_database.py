import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database.models import Order, Question
from app.database.session import Base, SQLITE_URL
from app.services.orders import OrderService


TEST_SQLITE_URL = "sqlite+aiosqlite:///:memory:"


def test_application_uses_sqlite_database():
    assert SQLITE_URL == "sqlite+aiosqlite:///./data/bot.db"


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(
        TEST_SQLITE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine):
    session_factory = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session


@pytest.mark.asyncio
async def test_create_order(test_session):
    order = await OrderService.create_order(
        test_session,
        {
            "order_number": "ORD-TEST-001",
            "telegram_user_id": 123456789,
            "telegram_username": "test_user",
            "telegram_first_name": "Тест",
            "source": "direct",
            "product_id": "coffee_table_from_video",
            "product_name": "Журнальный столик",
            "city": "Москва",
            "customer_name": "Иван",
            "contact": "+79991234567",
            "status": "new",
        },
    )

    assert order.id is not None
    assert order.order_number == "ORD-TEST-001"
    assert order.status == "new"


@pytest.mark.asyncio
async def test_create_question(test_session):
    question = await OrderService.create_question(
        test_session,
        {
            "telegram_user_id": 123456789,
            "telegram_username": "test_user",
            "text": "Есть ли товар в наличии?",
            "status": "new",
        },
    )

    assert question.id is not None
    assert question.text == "Есть ли товар в наличии?"
    assert question.status == "new"


@pytest.mark.asyncio
async def test_get_order_by_number(test_session):
    await OrderService.create_order(
        test_session,
        {
            "order_number": "ORD-TEST-002",
            "telegram_user_id": 987654321,
            "product_id": "napkin_holder",
            "product_name": "Салфетница",
            "city": "Казань",
            "customer_name": "Анна",
            "contact": "@anna",
        },
    )

    order = await OrderService.get_order_by_number(test_session, "ORD-TEST-002")

    assert order is not None
    assert order.city == "Казань"
    assert order.customer_name == "Анна"


@pytest.mark.asyncio
async def test_nullable_order_fields(test_session):
    order = await OrderService.create_order(
        test_session,
        {
            "order_number": "ORD-TEST-003",
            "telegram_user_id": 111111111,
            "product_id": "ginori_cups",
            "product_name": "Чашки Ginori",
            "city": "Москва",
            "customer_name": "Мария",
            "contact": "@maria",
        },
    )

    assert order.size is None
    assert order.color is None
    assert order.total_price is None
