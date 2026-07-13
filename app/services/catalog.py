import json
from pathlib import Path
from typing import Optional


PRODUCTS_FILE = Path(__file__).parent.parent.parent / "data" / "products.json"


def load_products() -> list[dict]:
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_products(products: list[dict]) -> None:
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


def get_product_by_id(product_id: str) -> Optional[dict]:
    products = load_products()
    for product in products:
        if product["id"] == product_id:
            return product
    return None


def get_active_products() -> list[dict]:
    products = load_products()
    return [p for p in products if p.get("is_active", False)]
