import pytest
import pytest_asyncio
import asyncio
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.session import Base
from app.database.session import _normalize_database_url
from app.database.models import Order, Question


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


def test_normalize_railway_postgres_url():
    url = "postgresql://user:test-secret@postgres.railway.internal:5432/railway"

    assert _normalize_database_url(url) == (
        "postgresql+asyncpg://user:test-secret@postgres.railway.internal:5432/railway"
    )


def test_normalize_empty_database_url():
    with pytest.raises(ValueError, match="DATABASE_URL задан пустым"):
        _normalize_database_url("  ")


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine):
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def order_service():
    from app.services.orders import OrderService
    return OrderService


@pytest.mark.asyncio
async def test_create_order(test_session, order_service):
    order_data = {
        "order_number": "ORD-TEST-001",
        "telegram_user_id": 123456789,
        "telegram_username": "test_user",
        "telegram_first_name": "Test",
        "source": "direct",
        "product_id": "coffee_table",
        "product_name": "Журнальный столик",
        "size": "80x60",
        "color": "белый",
        "city": "Москва",
        "customer_name": "Иван",
        "contact": "+79991234567",
        "comment": "Тестовый заказ",
        "product_price": 10000,
        "service_fee": 2000,
        "delivery_price": 3000,
        "total_price": 15000,
        "status": "new",
    }

    order = await order_service.create_order(test_session, order_data)

    assert order.id is not None
    assert order.order_number == "ORD-TEST-001"
    assert order.telegram_user_id == 123456789
    assert order.customer_name == "Иван"
    assert order.status == "new"


@pytest.mark.asyncio
async def test_create_question(test_session, order_service):
    question_data = {
        "telegram_user_id": 123456789,
        "telegram_username": "test_user",
        "text": "Есть ли этот товар в наличии?",
        "status": "new",
    }

    question = await order_service.create_question(test_session, question_data)

    assert question.id is not None
    assert question.text == "Есть ли этот товар в наличии?"
    assert question.status == "new"


@pytest.mark.asyncio
async def test_order_to_dict(test_session, order_service):
    order_data = {
        "order_number": "ORD-TEST-002",
        "telegram_user_id": 987654321,
        "telegram_username": "another_user",
        "telegram_first_name": "Пётр",
        "source": "instagram_table",
        "product_id": "ginori_cups",
        "product_name": "Чашки Ginori",
        "city": "Санкт-Петербург",
        "customer_name": "Пётр",
        "contact": "@petr",
        "status": "new",
    }

    order = await order_service.create_order(test_session, order_data)
    order_dict = order.to_dict()

    assert order_dict["order_number"] == "ORD-TEST-002"
    assert order_dict["source"] == "instagram_table"
    assert order_dict["product_name"] == "Чашки Ginori"
    assert order_dict["telegram_user_id"] == 987654321


@pytest.mark.asyncio
async def test_get_order_by_number(test_session, order_service):
    order_data = {
        "order_number": "ORD-TEST-003",
        "telegram_user_id": 111111111,
        "product_id": "napkin_holder",
        "product_name": "Салфетница",
        "city": "Казань",
        "customer_name": "Анна",
        "contact": "+79990000000",
        "status": "new",
    }

    await order_service.create_order(test_session, order_data)
    order = await order_service.get_order_by_number(test_session, "ORD-TEST-003")

    assert order is not None
    assert order.customer_name == "Анна"
    assert order.city == "Казань"


@pytest.mark.asyncio
async def test_order_with_nullable_fields(test_session, order_service):
    order_data = {
        "order_number": "ORD-TEST-004",
        "telegram_user_id": 222222222,
        "product_id": "custom",
        "product_name": "Кастомный товар",
        "city": "Москва",
        "customer_name": "Тест",
        "contact": "test@test.com",
        "size": None,
        "color": None,
        "comment": None,
        "custom_request": None,
        "custom_image_file_id": None,
        "product_price": None,
        "service_fee": None,
        "delivery_price": None,
        "total_price": None,
        "status": "new",
    }

    order = await order_service.create_order(test_session, order_data)

    assert order.size is None
    assert order.color is None
    assert order.total_price is None
    assert order.custom_image_file_id is None


@pytest.mark.asyncio
async def test_order_default_status(test_session, order_service):
    order_data = {
        "order_number": "ORD-TEST-005",
        "telegram_user_id": 333333333,
        "product_id": "test",
        "product_name": "Тест",
        "city": "Тест",
        "customer_name": "Тест",
        "contact": "test",
    }

    order = await order_service.create_order(test_session, order_data)

    assert order.status == "new"
