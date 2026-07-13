WELCOME = """Привет! 👋

Здесь можно заказать мебель и предметы интерьера из Китая — в том числе тот самый журнальный столик из видео.

Мы помогаем выкупить товар у поставщика и организуем его доставку в Россию.

Выберите товар, чтобы посмотреть фотографии, характеристики и предварительный расчёт стоимости 👇"""

HOW_IT_WORKS = """Как проходит заказ:

1. Вы выбираете товар из каталога или присылаете ссылку на нужную позицию.
2. Мы уточняем стоимость и наличие у поставщика.
3. Стоимость включает доставку товара до Москвы — доставка до двери оплачивается отдельно по факту доставки.
4. После подтверждения выкупаем товар и организуем доставку.
5. Примерный срок ожидания посылки — полтора месяца!"""

ASK_QUESTION_PROMPT = """Добрый день! Если у Вас остались вопросы, напишите их здесь.

Если вы хотите заказать какой-то конкретный товар, пришлите ссылку или фотографию — подумаем, что с этим сделать."""

QUESTION_CONFIRMED = """Ваш вопрос отправлен! ✅

Мы ответим вам в ближайшее время."""

HELP_TEXT = """📖 <b>Справка</b>

<b>Основные команды:</b>
/start — Главное меню
/catalog — Каталог товаров
/help — Показать справку
/cancel — Отменить текущее оформление
/my_id — Показать ваш Telegram ID

<b>Как заказать:</b>
1. Откройте каталог
2. Выберите товар
3. Нажмите «Перейти к заказу»
4. Заполните данные
5. Подтвердите заявку

Если у вас есть вопросы, нажмите «Задать вопрос» в главном меню."""

CUSTOM_PRODUCT_PROMPT = "Пришлите ссылку на товар, фотографию или кратко опишите, что вы хотите заказать."

ORDER_SIZE_PROMPT = "Выберите размер:"

ORDER_COLOR_PROMPT = "Выберите цвет:"

ORDER_CITY_PROMPT = "Введите город доставки:"

ORDER_NAME_PROMPT = "Как к вам обращаться?"

ORDER_CONTACT_PROMPT = """Как с вами связаться?

Вы можете:
• Нажать кнопку «Отправить номер телефона» 📱
• Указать номер или другой контакт вручную

Если у вас есть Telegram username, мы сможем связаться с вами через него."""

ORDER_COMMENT_PROMPT = "Есть ли дополнительные пожелания к заказу?"

CUSTOM_SIZE_PROMPT = "Введите нужный размер:"

CUSTOM_COLOR_PROMPT = "Укажите нужный цвет:"

def get_product_card(product: dict) -> str:
    lines = [f"📦 <b>{product['name']}</b>", "", product["full_description"]]

    if product.get("dimensions"):
        lines.append("")
        lines.append(f"<b>Размеры:</b> {', '.join(product['dimensions'])}")

    if product.get("materials"):
        lines.append("")
        lines.append(f"<b>Материалы:</b> {', '.join(product['materials'])}")

    if product.get("available_colors"):
        lines.append("")
        lines.append(f"<b>Доступные цвета:</b> {', '.join(product['available_colors'])}")

    lines.extend(["", get_price_breakdown_text(product)])

    return "\n".join(lines)


def get_price_breakdown_text(product: dict) -> str:
    from app.services.pricing import format_price, format_yuan

    pricing = product.get("pricing") or {}
    lines = ["💰 <b>Предварительная стоимость:</b>"]

    if product.get("delivery_period"):
        lines.append(f"— доставка: {product['delivery_period']}")

    if pricing:
        lines.extend([
            "",
            f"Стоимость товара с доставкой до склада в Китае: <b>{format_yuan(pricing['supplier_total_cny'])}</b>",
            f"Товар на Taobao — {format_yuan(pricing['taobao_price_cny'])}",
            "Комиссия за выкуп и доставку до склада — "
            f"{format_yuan(pricing['purchase_and_china_delivery_fee_cny'])}",
            "",
            f"Стоимость с доставкой до Москвы: <b>{format_yuan(pricing['moscow_total_cny'])}</b>",
            f"Товар + комиссия — {format_yuan(pricing['supplier_total_cny'])}",
            f"Международная доставка — {format_yuan(pricing['international_delivery_cny'])}",
            "",
            f"Стоимость в рублях: <b>{format_price(pricing['moscow_total_rub'])}</b>",
            f"(при курсе {int(pricing['exchange_rate_rub_per_cny'])} ₽ за юань)",
        ])

    lines.extend([
        "",
        "ℹ️ Стоимость включает доставку до склада в Москве. Доставка от склада «до двери» оплачивается отдельно после получения груза в Москве.",
    ])

    return "\n".join(lines)


def get_order_review(
    product_name: str,
    size: str | None,
    color: str | None,
    city: str,
    customer_name: str,
    contact: str,
    comment: str | None,
    total_price: int | None,
    is_confirmed: bool,
    moscow_total_price: int | None = None,
    custom_request: str | None = None,
) -> str:
    from app.services.pricing import format_price

    lines = ["", "📋 <b>Проверьте данные заявки:</b>", ""]
    lines.append(f"<b>Товар:</b> {product_name}")

    if size:
        lines.append(f"<b>Размер:</b> {size}")

    if color:
        lines.append(f"<b>Цвет:</b> {color}")

    if custom_request:
        lines.append(f"<b>Описание:</b> {custom_request}")

    lines.extend([
        f"<b>Город доставки:</b> {city}",
        f"<b>Имя:</b> {customer_name}",
        f"<b>Контакт:</b> {contact}",
    ])

    if comment:
        lines.append(f"<b>Комментарий:</b> {comment}")

    lines.append("")

    if moscow_total_price is not None:
        lines.append(
            f"💰 <b>Стоимость с доставкой до Москвы:</b> {format_price(moscow_total_price)}"
        )
    else:
        lines.append("💰 <b>Предварительная стоимость:</b> будет рассчитана после уточнения")

    lines.extend([
        "",
        "ℹ️ Доставка от склада «до двери» оплачивается отдельно после получения груза в Москве.",
    ])

    return "\n".join(lines)


ORDER_CONFIRMED_TEXT = """✅ <b>Заявка №{order_number} принята!</b>

Мы уточним наличие товара, параметры упаковки и окончательную стоимость доставки.

После проверки заказа с вами свяжутся по указанному контакту."""

CANCEL_TEXT = "Оформление отменено. Вы можете начать заново или вернуться в каталог."

ERROR_TEXT = "Что-то пошло не так. Попробуйте ещё раз или вернитесь в главное меню."

CANCEL_ORDER_BUTTON = "Отменить оформление"
BACK_TO_MENU = "Главное меню"
BACK_TO_CATALOG = "Вернуться в каталог"
