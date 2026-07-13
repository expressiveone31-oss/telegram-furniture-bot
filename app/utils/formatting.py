from typing import Optional


def format_price(value: Optional[int | float]) -> str:
    if value is None:
        return "уточняется"
    return f"{int(value):,} ₽".replace(",", " ")


def format_price_inline(value: Optional[int | float]) -> str:
    if value is None:
        return "—"
    return f"{int(value):,} ₽".replace(",", " ")
