import logging

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards import get_question_keyboard, get_cancel_keyboard, get_main_menu_keyboard
from app.texts import ASK_QUESTION_PROMPT, QUESTION_CONFIRMED
from app.services.notifications import send_question_notification
from app.services.orders import OrderService
from app.states import QuestionForm
from app.database.repositories import get_session
from app.config import settings

logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "ask_question")
async def ask_question(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        ASK_QUESTION_PROMPT,
        reply_markup=get_question_keyboard(settings.manager_url),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "leave_question")
async def leave_question(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QuestionForm.AWAITING_QUESTION)
    await callback.message.edit_text(
        "Напишите ваш вопрос:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(QuestionForm.AWAITING_QUESTION, F.text)
async def handle_question_text(message: Message, state: FSMContext, bot: Bot):
    text = message.text.strip()

    if not text:
        await message.answer(
            "Пожалуйста, напишите ваш вопрос.",
            reply_markup=get_cancel_keyboard()
        )
        return

    user = message.from_user

    question_data = {
        "telegram_user_id": user.id,
        "telegram_username": user.username,
        "text": text,
        "status": "new",
    }

    try:
        async for session in get_session():
            await OrderService.create_question(session, question_data)
            break
    except Exception as e:
        logger.error(f"Ошибка сохранения вопроса: {e}")

    try:
        await send_question_notification(bot, question_data)
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления о вопросе: {e}")

    await state.clear()

    await message.answer(
        QUESTION_CONFIRMED,
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "cancel_question")
async def cancel_question(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Вопрос отменён.",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()
