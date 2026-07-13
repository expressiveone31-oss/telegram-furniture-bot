from typing import Optional


def format_price(value: Optional[int | float]) -> str:
    if value is None:
        return "уточняется"
    return f"{int(value):,} ₽".replace(",", " ")


def format_yuan(value: int | float) -> str:
    return f"{int(value):,} ¥".replace(",", " ")


def get_moscow_total_rub(product: dict) -> Optional[int]:
    pricing = product.get("pricing") or {}
    value = pricing.get("moscow_total_rub")
    return int(value) if value is not None else None


def calculate_total(
    product_price: Optional[int | float] = None,
    service_fee: Optional[int | float] = None,
    delivery_price: Optional[int | float] = None,
) -> tuple[Optional[int], bool]:
    prices = []
    for price in [product_price, service_fee, delivery_price]:
        if price is not None:
            prices.append(price)

    if not prices:
        return None, False

    total = sum(prices)
    return int(total), True


def get_price_breakdown(product: dict) -> dict:
    product_price = product.get("product_price")
    service_fee = product.get("service_fee")
    delivery_price = product.get("delivery_price")

    total, is_confirmed = calculate_total(product_price, service_fee, delivery_price)

    return {
        "product_price": product_price,
        "service_fee": service_fee,
        "delivery_price": delivery_price,
        "total": total,
        "is_confirmed": is_confirmed,
    }
