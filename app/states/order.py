from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


class OrderForm(StatesGroup):
    START = State()
    AWAITING_CUSTOM_REQUEST = State()
    AWAITING_SIZE = State()
    AWAITING_SIZE_CUSTOM = State()
    AWAITING_COLOR = State()
    AWAITING_COLOR_CUSTOM = State()
    AWAITING_CITY = State()
    AWAITING_NAME = State()
    AWAITING_CONTACT = State()
    AWAITING_COMMENT = State()
    AWAITING_COMMENT_TEXT = State()
    REVIEW = State()
    EDITING = State()


class QuestionForm(StatesGroup):
    AWAITING_QUESTION = State()
