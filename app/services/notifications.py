import logging
from datetime import datetime
from typing import Optional

from aiogram import Bot

from app.config import settings

logger = logging.getLogger(__name__)


async def send_admin_notification(
    bot: Bot,
    order_data: dict,
    custom_image_file_id: Optional[str] = None,
) -> None:
    if not settings.admin_ids:
        logger.warning("ADMIN_TELEGRAM_IDS не настроен, уведомление не отправлено")
        return

    message = build_admin_notification_message(order_data)

    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=message,
                parse_mode="HTML",
            )
            logger.info(f"Уведомление о заявке {order_data.get('order_number')} отправлено админу {admin_id}")

            if custom_image_file_id:
                await bot.send_photo(
                    chat_id=admin_id,
                    photo=custom_image_file_id,
                    caption=f"Фото к заявке {order_data.get('order_number')}",
                )

        except Exception as e:
            logger.error(f"Ошибка отправки уведомления админу {admin_id}: {e}")


def build_admin_notification_message(order_data: dict) -> str:
    lines = [
        f"📋 <b>Новая заявка №{order_data.get('order_number')}</b>",
        "",
        f"Источник: {order_data.get('source', 'direct')}",
        f"Товар: {order_data.get('product_name')}",
    ]

    if order_data.get("size"):
        lines.append(f"Размер: {order_data.get('size')}")

    if order_data.get("color"):
        lines.append(f"Цвет: {order_data.get('color')}")

    lines.append(f"Город: {order_data.get('city')}")

    if order_data.get("total_price") is not None:
        from app.services.pricing import format_price
        lines.append(f"Предварительная стоимость: {format_price(order_data.get('total_price'))}")

    lines.extend([
        "",
        f"Имя клиента: {order_data.get('customer_name')}",
        f"Контакт: {order_data.get('contact')}",
    ])

    if order_data.get("telegram_username"):
        lines.append(f"Telegram: @{order_data.get('telegram_username')}")

    lines.append(f"Telegram ID: {order_data.get('telegram_user_id')}")

    if order_data.get("comment"):
        lines.extend(["", f"Комментарий: {order_data.get('comment')}"])

    if order_data.get("custom_request"):
        lines.extend(["", f"Описание товара: {order_data.get('custom_request')}"])

    return "\n".join(lines)


async def send_question_notification(bot: Bot, question_data: dict) -> None:
    if not settings.admin_ids:
        logger.warning("ADMIN_TELEGRAM_IDS не настроен, уведомление не отправлено")
        return

    message = build_question_notification_message(question_data)

    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=message,
                parse_mode="HTML",
            )
            logger.info(f"Уведомление о вопросе отправлено админу {admin_id}")
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления о вопросе админу {admin_id}: {e}")


def build_question_notification_message(question_data: dict) -> str:
    lines = [
        "❓ <b>Новый вопрос</b>",
        "",
        f"От: {question_data.get('telegram_username') or question_data.get('telegram_user_id')}",
        f"Telegram ID: {question_data.get('telegram_user_id')}",
        "",
        f"<b>Вопрос:</b>",
        question_data.get("text", ""),
    ]
    return "\n".join(lines)
