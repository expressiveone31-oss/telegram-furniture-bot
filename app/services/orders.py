import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Order, Question
from app.database.repositories import get_session

logger = logging.getLogger(__name__)


class OrderService:
    @staticmethod
    async def create_order(session: AsyncSession, order_data: dict) -> Order:
        order = Order(**order_data)
        session.add(order)
        await session.commit()
        await session.refresh(order)
        logger.info(f"Создана заявка {order.order_number}")
        return order

    @staticmethod
    async def create_question(session: AsyncSession, question_data: dict) -> Question:
        question = Question(**question_data)
        session.add(question)
        await session.commit()
        await session.refresh(question)
        logger.info(f"Создан вопрос от пользователя {question_data.get('telegram_user_id')}")
        return question

    @staticmethod
    async def get_order_by_number(session: AsyncSession, order_number: str) -> Optional[Order]:
        result = await session.execute(
            select(Order).where(Order.order_number == order_number)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_order_by_id(session: AsyncSession, order_id: int) -> Optional[Order]:
        result = await session.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()
