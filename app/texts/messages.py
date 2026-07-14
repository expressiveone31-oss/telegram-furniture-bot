WELCOME = """Привет! 👋

Здесь можно заказать мебель и предметы интерьера из Китая — в том числе тот самый журнальный столик из видео.

Мы помогаем выкупить товар у поставщика и организуем его доставку в Россию.

Выберите товар, чтобы посмотреть фотографии, характеристики и предварительный расчёт стоимости 👇"""

HOW_IT_WORKS = """📦 <b>Как оформить заказ</b>

<b>1. Оставьте заявку на понравившийся товар</b>

Для этого просто нажмите кнопку «Заказать».

<b>2. Мы связываемся с Вами</b>

Ответим на все вопросы, если они возникнут!

<b>3. Вы оплачиваете первый платёж</b>

После получения первого платежа мы выкупаем товар и организуем его доставку в Москву.

<b>4. Ждём доставку</b>

Средний срок доставки до склада в Москве — около 45–65 дней.

<b>5. Вы оплачиваете второй платёж</b>

После поступления товара в Москву вы оплачиваете оставшуюся стоимость заказа и доставку по России до вашего адреса.

<b>6. Получаете свой заказ</b>

Мы передаём товар в транспортную компанию, после чего он отправляется в ваш город.

🤍 <b>Важно</b>

• Все товары выкупаются специально под ваш заказ.

• Первый платёж используется для выкупа товара у продавца в Китае. Поскольку каждый товар приобретается специально под ваш заказ, после его отправки со склада в Китае отменить заказ или вернуть товар уже невозможно. Именно поэтому мы просим внести стоимость товара до оформления заказа.

• Стоимость в карточках товаров уже включает международную доставку до склада в Москве. Отдельно оплачивается только доставка по России до вашего адреса."""

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
        label = "Материал" if len(product["materials"]) == 1 else "Материалы"
        lines.append(f"<b>{label}:</b> {', '.join(product['materials'])}")

    if product.get("available_colors"):
        lines.append("")
        lines.append(f"<b>Доступные цвета:</b> {', '.join(product['available_colors'])}")

    lines.extend(["", get_price_breakdown_text(product)])

    return "\n".join(lines)


def get_price_breakdown_text(product: dict) -> str:
    from app.services.pricing import format_price, format_yuan

    pricing = product.get("pricing") or {}
    lines = ["💰 <b>Стоимость</b>"]

    if product.get("delivery_period"):
        lines.extend(["", f"⏳ <b>Срок доставки:</b> {product['delivery_period']}"])

    if pricing:
        lines.extend([
            "",
            f"Стоимость товара с доставкой до склада в Китае — <b>{format_yuan(pricing['supplier_total_cny'])}</b>",
            f"Товар на Taobao — {format_yuan(pricing['taobao_price_cny'])}",
            "Организация выкупа и доставки — "
            f"{format_yuan(pricing['purchase_and_china_delivery_fee_cny'])}",
            "",
            f"Стоимость с доставкой до Москвы — <b>{format_yuan(pricing['moscow_total_cny'])}</b>",
            f"Международная доставка — {format_yuan(pricing['international_delivery_cny'])}",
            "",
            f"💵 <b>Итого до склада в Москве — {format_price(pricing['moscow_total_rub'])}</b>",
            "",
            "💳 <b>Как происходит оплата</b>",
            "",
            f"Первый платеж — <b>{format_price(pricing['first_payment_rub'])}</b>",
            pricing["first_payment_description"],
            "",
            f"Второй платеж — <b>{format_price(pricing['second_payment_rub'])}</b>",
            "Оплачивается после поступления товара в Москву.",
        ])

    lines.extend([
        "",
        "ℹ️ Стоимость доставки по России зависит от вашего города и рассчитывается после поступления товара в Москву.",
        "",
        "🤍 <b>Важно:</b> все товары выкупаются специально под ваш заказ. Перед выкупом мы подтверждаем актуальную стоимость товара на Taobao и после вашего согласования сразу оформляем заказ.",
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
    first_payment_price: int | None = None,
    second_payment_price: int | None = None,
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
        if first_payment_price is not None:
            lines.append(f"<b>Первый платеж:</b> {format_price(first_payment_price)}")
        if second_payment_price is not None:
            lines.append(f"<b>Второй платеж:</b> {format_price(second_payment_price)}")
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
