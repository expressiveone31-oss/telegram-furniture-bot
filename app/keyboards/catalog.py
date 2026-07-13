from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_catalog_keyboard(products: List[dict]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for product in products:
        builder.row(
            InlineKeyboardButton(
                text=f"📦 {product['name']}",
                callback_data=f"product_{product['id']}"
            )
        )

    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
    )

    return builder.as_markup()


def get_product_keyboard(product_id: str, is_custom: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text="🛒 Перейти к заказу",
            callback_data=f"order_start_{product_id}"
        )
    )

    builder.row(
        InlineKeyboardButton(text="📦 Выбрать другой товар", callback_data="catalog"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
    )

    return builder.as_markup()
