import logging
import re
from datetime import datetime
from typing import Optional

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, PhotoSize
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.keyboards import (
    get_order_size_keyboard,
    get_order_color_keyboard,
    get_contact_keyboard,
    get_order_comment_keyboard,
    get_order_review_keyboard,
    get_edit_fields_keyboard,
    get_post_order_keyboard,
    get_cancel_keyboard,
    get_main_menu_keyboard,
    get_product_keyboard,
)
from app.texts import (
    CUSTOM_PRODUCT_PROMPT,
    ORDER_SIZE_PROMPT,
    ORDER_COLOR_PROMPT,
    ORDER_CITY_PROMPT,
    ORDER_NAME_PROMPT,
    ORDER_CONTACT_PROMPT,
    ORDER_COMMENT_PROMPT,
    CUSTOM_SIZE_PROMPT,
    CUSTOM_COLOR_PROMPT,
    get_order_review,
    ORDER_CONFIRMED_TEXT,
    ERROR_TEXT,
)
from app.services.catalog import get_product_by_id, get_active_products
from app.services.pricing import calculate_total, format_price
from app.services.notifications import send_admin_notification
from app.services.orders import OrderService
from app.states import OrderForm
from app.utils.order_numbers import generate_order_number
from app.database.repositories import get_session
from app.config import settings

logger = logging.getLogger(__name__)

router = Router()


def extract_text_from_message(message: Message) -> str:
    if message.text:
        return message.text.strip()
    if message.caption:
        return message.caption.strip()
    return ""


def validate_contact(contact: str) -> bool:
    cleaned = re.sub(r"[\s\-\(\)\+]", "", contact)
    return cleaned.isdigit() and len(cleaned) >= 7


async def update_order_data(state: FSMContext, **kwargs):
    current_data = await state.get_data()
    await state.update_data(**kwargs)


async def get_current_state(state: FSMContext) -> dict:
    return await state.get_data()


async def send_review_message(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    total, is_confirmed = calculate_total(
        data.get("product_price"),
        data.get("service_fee"),
        data.get("delivery_price"),
    )

    review_text = get_order_review(
        product_name=data.get("product_name", ""),
        size=data.get("size"),
        color=data.get("color"),
        city=data.get("city", ""),
        customer_name=data.get("customer_name", ""),
        contact=data.get("contact", ""),
        comment=data.get("comment"),
        total_price=total,
        is_confirmed=is_confirmed,
        moscow_total_price=data.get("moscow_total_price"),
        first_payment_price=data.get("first_payment_price"),
        second_payment_price=data.get("second_payment_price"),
        custom_request=data.get("custom_request"),
    )

    has_size = data.get("has_sizes", False)
    has_color = data.get("has_colors", False)

    keyboard = get_order_review_keyboard()

    await callback.message.edit_text(
        review_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("order_start_"))
async def order_start(callback: CallbackQuery, state: FSMContext):
    product_id = callback.data.replace("order_start_", "")

    product = get_product_by_id(product_id)

    if not product:
        await callback.message.edit_text(
            "Товар не найден.",
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()
        return

    await state.update_data(
        product_id=product["id"],
        product_name=product["name"],
        product_price=product.get("product_price"),
        service_fee=product.get("service_fee"),
        delivery_price=product.get("delivery_price"),
        moscow_total_price=(product.get("pricing") or {}).get("moscow_total_rub"),
        first_payment_price=(product.get("pricing") or {}).get("first_payment_rub"),
        second_payment_price=(product.get("pricing") or {}).get("second_payment_rub"),
        has_sizes=bool(product.get("dimensions")),
        has_colors=bool(product.get("available_colors")),
        is_custom=product.get("is_custom", False),
        sizes=product.get("dimensions", []),
        colors=product.get("available_colors", []),
    )

    if product.get("is_custom", False):
        await state.set_state(OrderForm.AWAITING_CUSTOM_REQUEST)
        await callback.message.edit_text(
            CUSTOM_PRODUCT_PROMPT,
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
    elif product.get("dimensions"):
        await state.set_state(OrderForm.AWAITING_SIZE)
        keyboard = get_order_size_keyboard(product["dimensions"])
        await callback.message.edit_text(
            ORDER_SIZE_PROMPT,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    elif product.get("available_colors"):
        await state.set_state(OrderForm.AWAITING_COLOR)
        keyboard = get_order_color_keyboard(product["available_colors"])
        await callback.message.edit_text(
            ORDER_COLOR_PROMPT,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await state.set_state(OrderForm.AWAITING_CITY)
        await callback.message.edit_text(
            ORDER_CITY_PROMPT,
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )

    await callback.answer()


@router.message(OrderForm.AWAITING_CUSTOM_REQUEST, F.photo)
async def handle_custom_request_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    await state.update_data(
        custom_image_file_id=photo.file_id,
        custom_request=message.caption or "Фото товара"
    )
    await process_custom_request_complete(message, state)


@router.message(OrderForm.AWAITING_CUSTOM_REQUEST, F.text)
async def handle_custom_request_text(message: Message, state: FSMContext):
    text = extract_text_from_message(message)

    if not text:
        await message.answer(
            "Пожалуйста, отправьте ссылку, описание или фотографию товара.",
            reply_markup=get_cancel_keyboard()
        )
        return

    await state.update_data(custom_request=text)
    await process_custom_request_complete(message, state)


async def process_custom_request_complete(message: Message, state: FSMContext):
    data = await state.get_data()

    if data.get("has_sizes"):
        await state.set_state(OrderForm.AWAITING_SIZE)
        keyboard = get_order_size_keyboard(data.get("sizes", []))
        await message.answer(ORDER_SIZE_PROMPT, reply_markup=keyboard, parse_mode="HTML")
    elif data.get("has_colors"):
        await state.set_state(OrderForm.AWAITING_COLOR)
        keyboard = get_order_color_keyboard(data.get("colors", []))
        await message.answer(ORDER_COLOR_PROMPT, reply_markup=keyboard, parse_mode="HTML")
    else:
        await state.set_state(OrderForm.AWAITING_CITY)
        await message.answer(ORDER_CITY_PROMPT, reply_markup=get_cancel_keyboard(), parse_mode="HTML")


@router.callback_query(F.data.startswith("size_"), OrderForm.AWAITING_SIZE)
async def handle_size(callback: CallbackQuery, state: FSMContext):
    size = callback.data.replace("size_", "")
    await state.update_data(size=size)

    data = await state.get_data()

    if data.get("has_colors"):
        await state.set_state(OrderForm.AWAITING_COLOR)
        keyboard = get_order_color_keyboard(data.get("colors", []))
        await callback.message.edit_text(
            ORDER_COLOR_PROMPT,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await state.set_state(OrderForm.AWAITING_CITY)
        await callback.message.edit_text(
            ORDER_CITY_PROMPT,
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )

    await callback.answer()


@router.callback_query(F.data == "order_custom_size", OrderForm.AWAITING_SIZE)
async def handle_custom_size_request(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderForm.AWAITING_SIZE_CUSTOM)
    await callback.message.edit_text(
        CUSTOM_SIZE_PROMPT,
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(OrderForm.AWAITING_SIZE_CUSTOM, F.text)
async def handle_custom_size(message: Message, state: FSMContext):
    text = extract_text_from_message(message)
    if not text:
        await message.answer("Введите размер:")
        return

    await state.update_data(size=text)
    data = await state.get_data()

    if data.get("has_colors"):
        await state.set_state(OrderForm.AWAITING_COLOR)
        keyboard = get_order_color_keyboard(data.get("colors", []))
        await message.answer(ORDER_COLOR_PROMPT, reply_markup=keyboard, parse_mode="HTML")
    else:
        await state.set_state(OrderForm.AWAITING_CITY)
        await message.answer(ORDER_CITY_PROMPT, reply_markup=get_cancel_keyboard(), parse_mode="HTML")


@router.callback_query(F.data.startswith("color_"), OrderForm.AWAITING_COLOR)
async def handle_color(callback: CallbackQuery, state: FSMContext):
    color = callback.data.replace("color_", "")
    await state.update_data(color=color)
    await state.set_state(OrderForm.AWAITING_CITY)

    await callback.message.edit_text(
        ORDER_CITY_PROMPT,
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "order_custom_color", OrderForm.AWAITING_COLOR)
async def handle_custom_color_request(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderForm.AWAITING_COLOR_CUSTOM)
    await callback.message.edit_text(
        CUSTOM_COLOR_PROMPT,
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "order_skip_color", OrderForm.AWAITING_COLOR)
async def handle_skip_color(callback: CallbackQuery, state: FSMContext):
    await state.update_data(color=None)
    await state.set_state(OrderForm.AWAITING_CITY)

    await callback.message.edit_text(
        ORDER_CITY_PROMPT,
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(OrderForm.AWAITING_COLOR_CUSTOM, F.text)
async def handle_custom_color(message: Message, state: FSMContext):
    text = extract_text_from_message(message)
    if not text:
        await message.answer("Укажите цвет:")
        return

    await state.update_data(color=text)
    await state.set_state(OrderForm.AWAITING_CITY)
    await message.answer(ORDER_CITY_PROMPT, reply_markup=get_cancel_keyboard(), parse_mode="HTML")


@router.message(OrderForm.AWAITING_CITY, F.text)
async def handle_city(message: Message, state: FSMContext):
    text = extract_text_from_message(message)
    if not text:
        await message.answer(ORDER_CITY_PROMPT, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
        return

    await state.update_data(city=text)
    await state.set_state(OrderForm.AWAITING_NAME)

    await message.answer(ORDER_NAME_PROMPT, reply_markup=get_cancel_keyboard(), parse_mode="HTML")


@router.message(OrderForm.AWAITING_NAME, F.text)
async def handle_name(message: Message, state: FSMContext):
    text = extract_text_from_message(message)
    if not text:
        await message.answer(ORDER_NAME_PROMPT, reply_markup=get_cancel_keyboard(), parse_mode="HTML")
        return

    await state.update_data(customer_name=text)
    await state.set_state(OrderForm.AWAITING_CONTACT)

    contact_keyboard = get_contact_keyboard()

    username = message.from_user.username
    if username:
        await state.update_data(contact=f"@{username}")
        await state.set_state(OrderForm.AWAITING_COMMENT)
        await message.answer(
            ORDER_COMMENT_PROMPT,
            reply_markup=get_order_comment_keyboard(),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            ORDER_CONTACT_PROMPT,
            reply_markup=contact_keyboard,
            parse_mode="HTML"
        )


@router.message(OrderForm.AWAITING_CONTACT, F.contact)
async def handle_contact(message: Message, state: FSMContext):
    contact = message.contact
    contact_str = contact.phone_number or str(contact.user_id)
    await state.update_data(contact=contact_str)
    await state.set_state(OrderForm.AWAITING_COMMENT)

    await message.answer(
        ORDER_COMMENT_PROMPT,
        reply_markup=get_order_comment_keyboard(),
        parse_mode="HTML"
    )


@router.message(OrderForm.AWAITING_CONTACT, F.text)
async def handle_contact_text(message: Message, state: FSMContext):
    text = extract_text_from_message(message)
    if not text:
        await message.answer(
            ORDER_CONTACT_PROMPT,
            reply_markup=get_contact_keyboard(),
            parse_mode="HTML"
        )
        return

    await state.update_data(contact=text)
    await state.set_state(OrderForm.AWAITING_COMMENT)

    await message.answer(
        ORDER_COMMENT_PROMPT,
        reply_markup=get_order_comment_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "order_skip_comment", OrderForm.AWAITING_COMMENT)
async def handle_skip_comment(callback: CallbackQuery, state: FSMContext):
    await state.update_data(comment=None)
    await state.set_state(OrderForm.REVIEW)

    await send_review_message(callback, state)


@router.callback_query(F.data == "order_add_comment", OrderForm.AWAITING_COMMENT)
async def handle_add_comment(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderForm.AWAITING_COMMENT_TEXT)
    await callback.message.edit_text(
        "Введите ваш комментарий:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(OrderForm.AWAITING_COMMENT_TEXT, F.text)
async def handle_comment_text(message: Message, state: FSMContext):
    text = extract_text_from_message(message)
    await state.update_data(comment=text)
    await state.set_state(OrderForm.REVIEW)

    data = await state.get_data()

    total, is_confirmed = calculate_total(
        data.get("product_price"),
        data.get("service_fee"),
        data.get("delivery_price"),
    )

    review_text = get_order_review(
        product_name=data.get("product_name", ""),
        size=data.get("size"),
        color=data.get("color"),
        city=data.get("city", ""),
        customer_name=data.get("customer_name", ""),
        contact=data.get("contact", ""),
        comment=text,
        total_price=total,
        is_confirmed=is_confirmed,
        moscow_total_price=data.get("moscow_total_price"),
        first_payment_price=data.get("first_payment_price"),
        second_payment_price=data.get("second_payment_price"),
        custom_request=data.get("custom_request"),
    )

    await message.answer(
        review_text,
        reply_markup=get_order_review_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "order_review", OrderForm.REVIEW)
async def review_order(callback: CallbackQuery, state: FSMContext):
    await send_review_message(callback, state)


@router.callback_query(F.data == "order_edit", OrderForm.REVIEW)
async def edit_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    keyboard = get_edit_fields_keyboard(
        has_size=data.get("has_sizes", False),
        has_color=data.get("has_colors", False),
    )

    await state.set_state(OrderForm.EDITING)
    await callback.message.edit_text(
        "Что вы хотите изменить?",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


async def handle_edit_field(callback: CallbackQuery, state: FSMContext, field: str, prompt: str, state_to_set):
    await state.set_state(state_to_set)
    await callback.message.edit_text(
        prompt,
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "order_edit_size", OrderForm.EDITING)
async def edit_size(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    sizes = data.get("sizes", [])

    if sizes:
        keyboard = get_order_size_keyboard(sizes)
        await state.set_state(OrderForm.AWAITING_SIZE)
        await callback.message.edit_text(
            ORDER_SIZE_PROMPT,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await state.set_state(OrderForm.AWAITING_SIZE_CUSTOM)
        await callback.message.edit_text(
            CUSTOM_SIZE_PROMPT,
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
    await callback.answer()


@router.callback_query(F.data == "order_edit_color", OrderForm.EDITING)
async def edit_color(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    colors = data.get("colors", [])

    if colors:
        keyboard = get_order_color_keyboard(colors)
        await state.set_state(OrderForm.AWAITING_COLOR)
        await callback.message.edit_text(
            ORDER_COLOR_PROMPT,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    else:
        await state.set_state(OrderForm.AWAITING_COLOR_CUSTOM)
        await callback.message.edit_text(
            CUSTOM_COLOR_PROMPT,
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
    await callback.answer()


@router.callback_query(F.data == "order_edit_city", OrderForm.EDITING)
async def edit_city(callback: CallbackQuery, state: FSMContext):
    await handle_edit_field(callback, state, "city", ORDER_CITY_PROMPT, OrderForm.AWAITING_CITY)


@router.callback_query(F.data == "order_edit_name", OrderForm.EDITING)
async def edit_name(callback: CallbackQuery, state: FSMContext):
    await handle_edit_field(callback, state, "name", ORDER_NAME_PROMPT, OrderForm.AWAITING_NAME)


@router.callback_query(F.data == "order_edit_contact", OrderForm.EDITING)
async def edit_contact(callback: CallbackQuery, state: FSMContext):
    await handle_edit_field(callback, state, "contact", ORDER_CONTACT_PROMPT, OrderForm.AWAITING_CONTACT)


@router.callback_query(F.data == "order_edit_comment", OrderForm.EDITING)
async def edit_comment(callback: CallbackQuery, state: FSMContext):
    await handle_edit_field(callback, state, "comment", "Введите комментарий:", OrderForm.AWAITING_COMMENT_TEXT)


@router.callback_query(F.data == "order_confirm", OrderForm.REVIEW)
async def confirm_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()

    order_number = generate_order_number()

    total, _ = calculate_total(
        data.get("product_price"),
        data.get("service_fee"),
        data.get("delivery_price"),
    )

    user = callback.from_user

    order_data = {
        "order_number": order_number,
        "telegram_user_id": user.id,
        "telegram_username": user.username,
        "telegram_first_name": user.first_name,
        "source": data.get("source", "direct"),
        "product_id": data.get("product_id", ""),
        "product_name": data.get("product_name", ""),
        "size": data.get("size"),
        "color": data.get("color"),
        "city": data.get("city", ""),
        "customer_name": data.get("customer_name", ""),
        "contact": data.get("contact", ""),
        "comment": data.get("comment"),
        "custom_request": data.get("custom_request"),
        "custom_image_file_id": data.get("custom_image_file_id"),
        "product_price": data.get("product_price"),
        "service_fee": data.get("service_fee"),
        "delivery_price": data.get("delivery_price"),
        "total_price": total,
        "status": "new",
    }

    try:
        async for session in get_session():
            await OrderService.create_order(session, order_data)
            break
    except Exception as e:
        logger.error(f"Ошибка сохранения заказа: {e}")
        await callback.message.edit_text(
            ERROR_TEXT,
            reply_markup=get_main_menu_keyboard()
        )
        await callback.answer()
        return

    try:
        await send_admin_notification(
            bot,
            order_data,
            data.get("custom_image_file_id"),
        )
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления админу: {e}")

    await state.clear()

    confirmation_text = ORDER_CONFIRMED_TEXT.format(order_number=order_number)

    await callback.message.edit_text(
        confirmation_text,
        reply_markup=get_post_order_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "order_cancel")
async def cancel_order(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    from app.texts import CANCEL_TEXT
    await callback.message.edit_text(
        CANCEL_TEXT,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
