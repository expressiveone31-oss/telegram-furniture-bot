from app.keyboards.main import get_main_menu_keyboard, get_back_keyboard
from app.keyboards.catalog import get_catalog_keyboard, get_product_keyboard
from app.keyboards.order import (
    get_order_size_keyboard,
    get_order_color_keyboard,
    get_contact_keyboard,
    get_order_comment_keyboard,
    get_order_review_keyboard,
    get_edit_fields_keyboard,
    get_post_order_keyboard,
    get_cancel_keyboard,
    get_question_keyboard,
)

__all__ = [
    "get_main_menu_keyboard",
    "get_back_keyboard",
    "get_catalog_keyboard",
    "get_product_keyboard",
    "get_order_size_keyboard",
    "get_order_color_keyboard",
    "get_contact_keyboard",
    "get_order_comment_keyboard",
    "get_order_review_keyboard",
    "get_edit_fields_keyboard",
    "get_post_order_keyboard",
    "get_cancel_keyboard",
    "get_question_keyboard",
]
