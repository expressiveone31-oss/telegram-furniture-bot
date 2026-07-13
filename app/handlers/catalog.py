import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.keyboards import get_catalog_keyboard, get_product_keyboard, get_main_menu_keyboard
from app.texts import get_product_card
from app.services.catalog import get_active_products, get_product_by_id

logger = logging.getLogger(__name__)

router = Router()


CATALOG_TITLE = "📦 <b>Каталог товаров:</b>\n\nВыберите товар:"
CATALOG_EMPTY = "Каталог временно пуст. Скоро здесь появятся товары!"


@router.message(Command("catalog"))
async def cmd_catalog(message: Message, state: FSMContext):
    products = get_active_products()

    if not products:
        await message.answer(CATALOG_EMPTY, reply_markup=get_main_menu_keyboard())
        return

    await message.answer(
        CATALOG_TITLE,
        reply_markup=get_catalog_keyboard(products),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "catalog")
async def show_catalog_callback(callback: CallbackQuery, state: FSMContext):
    products = get_active_products()

    if not products:
        await callback.message.edit_text(CATALOG_EMPTY, reply_markup=get_main_menu_keyboard())
        await callback.answer()
        return

    try:
        await callback.message.edit_text(
            CATALOG_TITLE,
            reply_markup=get_catalog_keyboard(products),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.answer(
            CATALOG_TITLE,
            reply_markup=get_catalog_keyboard(products),
            parse_mode="HTML"
        )

    await callback.answer()


@router.callback_query(F.data.startswith("product_"))
async def show_product(callback: CallbackQuery, state: FSMContext):
    product_id = callback.data.replace("product_", "")

    product = get_product_by_id(product_id)

    if not product:
        await callback.message.edit_text(
            "Товар не найден. Попробуйте выбрать другой.",
            reply_markup=get_catalog_keyboard(get_active_products())
        )
        await callback.answer()
        return

    if not product.get("is_active", False):
        await callback.message.edit_text(
            "Этот товар временно недоступен. Выберите другой.",
            reply_markup=get_catalog_keyboard(get_active_products())
        )
        await callback.answer()
        return

    card_text = get_product_card(product)

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
    )

    try:
        await callback.message.edit_text(
            card_text,
            reply_markup=get_product_keyboard(product["id"], product.get("is_custom", False)),
            parse_mode="HTML"
        )
    except Exception:
        await callback.message.answer(
            card_text,
            reply_markup=get_product_keyboard(product["id"], product.get("is_custom", False)),
            parse_mode="HTML"
        )

    await callback.answer()
