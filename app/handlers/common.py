import logging

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, Update, ErrorEvent
from aiogram.fsm.context import FSMContext

from app.keyboards import get_main_menu_keyboard
from app.texts import ERROR_TEXT

logger = logging.getLogger(__name__)

router = Router()


@router.error()
async def error_handler(event: ErrorEvent):
    logger.error(f"Handler error: {event.exception}", exc_info=event.exception)

    update = event.update
    try:
        if update.message:
            await update.message.answer(
                ERROR_TEXT,
                reply_markup=get_main_menu_keyboard()
            )
        elif update.callback_query:
            await update.callback_query.answer(ERROR_TEXT, show_alert=True)
    except Exception as e:
        logger.error(f"Failed to send error message: {e}")

    return True


@router.message()
async def handle_unknown_message(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state:
        return

    await message.answer(
        "Я не понимаю это сообщение. Используйте кнопки меню или команды:\n\n"
        "/start — Главное меню\n"
        "/catalog — Каталог\n"
        "/help — Справка",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query()
async def handle_unknown_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer("Кнопка устарела. Попробуйте начать заново.")
