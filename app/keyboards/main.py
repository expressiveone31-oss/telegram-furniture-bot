from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.texts import BACK_TO_CATALOG, BACK_TO_MENU


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📚 Посмотреть каталог", callback_data="catalog"),
        InlineKeyboardButton(text="📦 Как оформить заказ", callback_data="how_it_works"),
        InlineKeyboardButton(text="❓ Задать вопрос", callback_data="ask_question"),
    )
    return builder.as_markup()


def get_back_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📚 Перейти в каталог", callback_data="catalog"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
    )
    return builder.as_markup()
