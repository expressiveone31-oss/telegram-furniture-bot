from typing import List, Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from app.texts import CANCEL_ORDER_BUTTON


def get_order_size_keyboard(sizes: List[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for size in sizes:
        builder.row(
            InlineKeyboardButton(text=size, callback_data=f"size_{size}")
        )

    builder.row(
        InlineKeyboardButton(text="📏 Нужен другой размер", callback_data="order_custom_size")
    )

    return builder.as_markup()


def get_order_color_keyboard(colors: List[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for color in colors:
        builder.row(
            InlineKeyboardButton(text=color, callback_data=f"color_{color}")
        )

    builder.row(
        InlineKeyboardButton(text="🎨 Другой цвет", callback_data="order_custom_color"),
        InlineKeyboardButton(text="❓ Пока не знаю", callback_data="order_skip_color"),
    )

    return builder.as_markup()


def get_contact_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_order_comment_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Нет, продолжить", callback_data="order_skip_comment"),
        InlineKeyboardButton(text="✏️ Добавить комментарий", callback_data="order_add_comment"),
    )
    builder.row(
        InlineKeyboardButton(text=CANCEL_ORDER_BUTTON, callback_data="order_cancel"),
    )
    return builder.as_markup()


def get_order_review_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить заявку", callback_data="order_confirm"),
    )
    builder.row(
        InlineKeyboardButton(text="✏️ Изменить данные", callback_data="order_edit"),
        InlineKeyboardButton(text=CANCEL_ORDER_BUTTON, callback_data="order_cancel"),
    )
    return builder.as_markup()


def get_edit_fields_keyboard(
    has_size: bool = False,
    has_color: bool = False,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if has_size:
        builder.row(
            InlineKeyboardButton(text="✏️ Изменить размер", callback_data="order_edit_size")
        )

    if has_color:
        builder.row(
            InlineKeyboardButton(text="✏️ Изменить цвет", callback_data="order_edit_color")
        )

    builder.row(
        InlineKeyboardButton(text="✏️ Изменить город", callback_data="order_edit_city"),
        InlineKeyboardButton(text="✏️ Изменить имя", callback_data="order_edit_name"),
    )
    builder.row(
        InlineKeyboardButton(text="✏️ Изменить контакт", callback_data="order_edit_contact"),
        InlineKeyboardButton(text="✏️ Изменить комментарий", callback_data="order_edit_comment"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Вернуться к проверке", callback_data="order_review"),
        InlineKeyboardButton(text=CANCEL_ORDER_BUTTON, callback_data="order_cancel"),
    )

    return builder.as_markup()


def get_post_order_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📚 Вернуться в каталог", callback_data="catalog"),
    )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
    )
    return builder.as_markup()


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=CANCEL_ORDER_BUTTON, callback_data="order_cancel"),
    )
    return builder.as_markup()


def get_question_keyboard(manager_url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✏️ Оставить вопрос", callback_data="leave_question"),
    )
    if manager_url:
        builder.row(
            InlineKeyboardButton(text="💬 Написать менеджеру", url=manager_url),
        )
    builder.row(
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
    )
    return builder.as_markup()
