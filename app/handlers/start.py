import logging
from typing import Optional

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext

from app.keyboards import get_main_menu_keyboard, get_back_keyboard
from app.texts import WELCOME, HOW_IT_WORKS, HELP_TEXT, ERROR_TEXT
from app.services.catalog import get_active_products
from app.states import QuestionForm

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject):
    await state.clear()

    source = command.args if command.args else "direct"

    await state.update_data(source=source)

    await message.answer(
        WELCOME,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        HELP_TEXT,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )


@router.message(Command("my_id"))
async def cmd_my_id(message: Message):
    await message.answer(
        f"Ваш Telegram ID: <code>{message.from_user.id}</code>",
        parse_mode="HTML"
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Оформление отменено. Вы можете начать заново.",
        reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await callback.message.edit_text(
        WELCOME,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "how_it_works")
async def callback_how_it_works(callback: CallbackQuery):
    await callback.message.edit_text(
        HOW_IT_WORKS,
        reply_markup=get_back_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
