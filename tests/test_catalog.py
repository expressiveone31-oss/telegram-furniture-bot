import pytest
import json
import os
from pathlib import Path

from app.services.catalog import load_products, get_active_products, get_product_by_id
from app.services.pricing import format_price, calculate_total, get_price_breakdown
from app.utils.order_numbers import generate_order_number


class TestCatalog:
    def test_load_products(self):
        products = load_products()
        assert isinstance(products, list)
        assert len(products) == 3

    def test_products_have_required_fields(self):
        products = load_products()
        required_fields = [
            "id", "name", "short_description", "full_description",
            "dimensions", "materials", "available_colors", "image",
            "product_price", "service_fee", "delivery_price",
            "delivery_period", "is_custom", "is_active"
        ]
        for product in products:
            for field in required_fields:
                assert field in product, f"Missing field '{field}' in product"

    def test_products_have_unique_ids(self):
        products = load_products()
        ids = [p["id"] for p in products]
        assert len(ids) == len(set(ids)), "Product IDs are not unique"

    def test_get_active_products(self):
        products = get_active_products()
        for product in products:
            assert product.get("is_active") is True

    def test_get_product_by_id(self):
        product = get_product_by_id("coffee_table_from_video")
        assert product is not None
        assert product["name"] == "Тот самый журнальный столик из видео"

    def test_get_product_by_id_not_found(self):
        product = get_product_by_id("nonexistent_product")
        assert product is None

    def test_inactive_product_filtered(self):
        products = load_products()
        inactive = [p for p in products if not p.get("is_active")]
        active = get_active_products()
        assert len(active) == len(products) - len(inactive)


class TestPricing:
    def test_format_price_with_value(self):
        assert format_price(1000) == "1 000 ₽"
        assert format_price(150000) == "150 000 ₽"
        assert format_price(0) == "0 ₽"

    def test_format_price_none(self):
        assert format_price(None) == "уточняется"

    def test_format_price_float(self):
        assert format_price(1500.5) == "1 500 ₽"

    def test_calculate_total_all_values(self):
        total, is_confirmed = calculate_total(1000, 200, 300)
        assert total == 1500
        assert is_confirmed is True

    def test_calculate_total_no_values(self):
        total, is_confirmed = calculate_total(None, None, None)
        assert total is None
        assert is_confirmed is False

    def test_calculate_total_partial(self):
        total, is_confirmed = calculate_total(1000, 200, None)
        assert total == 1200
        assert is_confirmed is True

    def test_calculate_total_none_product_price(self):
        total, is_confirmed = calculate_total(None, 200, 300)
        assert total == 500
        assert is_confirmed is True

    def test_get_price_breakdown(self):
        product = {
            "product_price": 1000,
            "service_fee": 200,
            "delivery_price": 300,
        }
        breakdown = get_price_breakdown(product)
        assert breakdown["product_price"] == 1000
        assert breakdown["service_fee"] == 200
        assert breakdown["delivery_price"] == 300
        assert breakdown["total"] == 1500
        assert breakdown["is_confirmed"] is True

    def test_get_price_breakdown_no_prices(self):
        product = {
            "product_price": None,
            "service_fee": None,
            "delivery_price": None,
        }
        breakdown = get_price_breakdown(product)
        assert breakdown["total"] is None
        assert breakdown["is_confirmed"] is False


class TestProductCard:
    def test_product_without_dimensions(self):
        product = get_product_by_id("coffee_table_from_video")
        assert product["dimensions"] == []

    def test_product_without_materials(self):
        product = get_product_by_id("coffee_table_from_video")
        assert product["materials"] == []

    def test_product_without_colors(self):
        product = get_product_by_id("coffee_table_from_video")
        assert product["available_colors"] == []

    def test_product_with_materials(self):
        product = get_product_by_id("ginori_cups")
        assert "фарфор" in product["materials"]

    def test_custom_product_has_flag(self):
        # После правок «Другой товар под заказ» удалён из каталога.
        # Проверяем, что в каталоге нет товаров с is_custom=True.
        products = load_products()
        assert all(not p.get("is_custom", False) for p in products)

    def test_regular_product_has_no_custom_flag(self):
        product = get_product_by_id("coffee_table_from_video")
        assert product["is_custom"] is False


class TestOrderNumber:
    def test_generate_order_number_format(self):
        order_number = generate_order_number()
        assert order_number.startswith("ORD-")
        parts = order_number.split("-")
        assert len(parts) == 3

    def test_generate_order_number_unique(self):
        import time
        numbers = []
        for _ in range(5):
            numbers.append(generate_order_number())
            time.sleep(0.001)
        assert len(numbers) == len(set(numbers))


class TestProductMessages:
    def test_coffee_table_price_breakdown(self):
        product = get_product_by_id("coffee_table_from_video")
        from app.texts.messages import get_price_breakdown_text
        text = get_price_breakdown_text(product)
        assert "Срок доставки:</b> ≈ 45 дней" in text
        assert "759 ¥" in text
        assert "459 ¥" in text
        assert "300 ¥" in text
        assert "2 329 ¥" in text
        assert "1 570 ¥" in text
        assert "30 300 ₽" in text
        assert "9 890 ₽" in text
        assert "20 410 ₽" in text
        assert "Организация выкупа и доставки" in text
        assert "Товар + организация выкупа и доставки" not in text
        assert "Как происходит оплата" in text
        assert "все товары выкупаются специально под ваш заказ" in text
        assert "при курсе" not in text
        assert "товар у поставщика: уточняется" not in text
        assert "комиссия за выкуп и сопровождение: уточняется" not in text

    def test_price_breakdown_text_without_prices(self):
        product = {
            "name": "Тестовый товар",
            "full_description": "Описание",
            "delivery_period": "уточняется",
            "product_price": None,
            "service_fee": None,
            "delivery_price": None,
        }
        from app.texts.messages import get_price_breakdown_text
        text = get_price_breakdown_text(product)
        assert "уточняется" in text

    def test_cups_and_napkin_holder_prices(self):
        from app.texts.messages import get_price_breakdown_text
        cups = get_price_breakdown_text(get_product_by_id("ginori_cups"))
        napkin_holder = get_price_breakdown_text(get_product_by_id("napkin_holder"))
        assert "456 ¥" in cups
        assert "5 928 ₽" in cups
        assert "1 950 ₽" in cups
        assert "3 978 ₽" in cups
        assert "562 ¥" in napkin_holder
        assert "7 306 ₽" in napkin_holder
        assert "2 600 ₽" in napkin_holder
        assert "4 706 ₽" in napkin_holder


class TestOrderReview:
    def test_review_with_all_fields(self):
        from app.texts.messages import get_order_review
        text = get_order_review(
            product_name="Журнальный столик",
            size="80x60",
            color="белый",
            city="Москва",
            customer_name="Иван",
            contact="+79991234567",
            comment="Доставка к подъезду",
            total_price=15000,
            is_confirmed=True,
            moscow_total_price=30160,
        )
        assert "Журнальный столик" in text
        assert "80x60" in text
        assert "белый" in text
        assert "Москва" in text
        assert "Иван" in text
        assert "+79991234567" in text
        assert "Доставка к подъезду" in text
        assert "Стоимость с доставкой до Москвы" in text
        assert "30 160 ₽" in text
        assert "до двери" in text

    def test_review_without_optional_fields(self):
        from app.texts.messages import get_order_review
        text = get_order_review(
            product_name="Чашки",
            size=None,
            color=None,
            city="Санкт-Петербург",
            customer_name="Мария",
            contact="@mariya",
            comment=None,
            total_price=None,
            is_confirmed=False,
        )
        assert "Чашки" in text
        assert "Санкт-Петербург" in text
        assert "Мария" in text
        assert "Размер" not in text
        assert "Цвет" not in text


class TestEmptyCharacteristics:
    def test_empty_dimensions_not_shown(self):
        product = get_product_by_id("coffee_table_from_video")
        from app.texts.messages import get_product_card
        text = get_product_card(product)
        assert "Размеры:" not in text

    def test_empty_materials_not_shown(self):
        product = get_product_by_id("coffee_table_from_video")
        from app.texts.messages import get_product_card
        text = get_product_card(product)
        assert "Материалы:" not in text

    def test_empty_colors_not_shown(self):
        product = get_product_by_id("coffee_table_from_video")
        from app.texts.messages import get_product_card
        text = get_product_card(product)
        assert "Цвета:" not in text
