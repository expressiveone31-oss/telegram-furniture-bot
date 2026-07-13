# Telegram-бот для заказа мебели и предметов интерьера из Китая

Telegram-бот для обработки заявок от клиентов, которые переходят из Instagram Reels и хотят заказать товары из Китая.

## Используемые технологии

- **Python 3.11+**
- **aiogram 3** — асинхронный фреймворк для Telegram Bot API
- **SQLAlchemy 2** с async — работа с базой данных
- **SQLite** — для локальной разработки
- **PostgreSQL** — для размещения на Railway
- **Docker** — контейнеризация
- **Railway** — хостинг

## Быстрый старт

### 1. Создание Telegram-бота

1. Откройте Telegram и найдите **@BotFather**
2. Отправьте команду `/newbot`
3. Следуйте инструкциям и сохраните полученный **токен**

### 2. Куда вставить токен Telegram-бота

> **Важно:** Никогда не вставляйте токен напрямую в код!

1. В корне проекта создайте файл `.env`
2. Скопируйте содержимое из `.env.example`
3. Замените `PASTE_TELEGRAM_BOT_TOKEN_HERE` на ваш токен:

```env
BOT_TOKEN=ВАШ_ТОКЕН_ОТ_BOTFATHER
ADMIN_TELEGRAM_IDS=123456789
MANAGER_URL=https://t.me/your_username
DATABASE_URL=sqlite+aiosqlite:///./data/bot.db
LOG_LEVEL=INFO
```

**Для Railway:** токен добавляется в раздел **Variables** проекта, а не в код и не в GitHub.

### 3. Как узнать ваш Telegram ID

1. Откройте Telegram и найдите **@userinfobot** (или **@getidsbot**)
2. Отправьте `/start`
3. Скопируйте число в поле **ID** — это ваш Telegram ID

Или используйте команду `/my_id` в боте после первого запуска.

### 4. Установка Python и зависимостей

#### macOS / Linux

```bash
# Проверьте версию Python
python3 --version  # должен быть 3.11 или выше

# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте виртуальное окружение
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

#### Windows

```cmd
# Проверьте версию Python
python --version

# Создайте виртуальное окружение
python -m venv venv

# Активируйте виртуальное окружение
venv\Scripts\activate

# Установите зависимости
pip install -r requirements.txt
```

### 5. Запуск проекта локально

```bash
# Убедитесь, что виртуальное окружение активировано
source venv/bin/activate  # Linux/macOS
# или
venv\Scripts\activate  # Windows

# Запустите бота
python -m app.main
```

Вы должны увидеть:
```
Бот запускается...
Бот готов к работе!
```

### 6. Запуск через Docker

```bash
# Создайте файл .env
cp .env.example .env
# Отредактируйте .env, добавив токен

# Запустите контейнер
docker-compose up --build
```

### 7. Запуск тестов

```bash
# Активируйте виртуальное окружение
source venv/bin/activate

# Запустите все тесты
pytest

# Запустите тесты с подробным выводом
pytest -v
```

## Настройка каталога товаров

Файл каталога: `data/products.json`

### Структура товара

```json
{
  "id": "unique_id",
  "name": "Название товара",
  "short_description": "Краткое описание",
  "full_description": "Полное описание",
  "dimensions": ["60x40", "80x60"],
  "materials": ["дерево", "металл"],
  "available_colors": ["белый", "чёрный"],
  "image": "file_id или URL",
  "product_price": 10000,
  "service_fee": 2000,
  "delivery_price": 3000,
  "delivery_period": "14-21 день",
  "is_custom": false,
  "is_active": true
}
```

### Как изменить цены

Откройте `data/products.json` и измените значения:
- `product_price` — стоимость товара у поставщика
- `service_fee` — комиссия за выкуп и сопровождение
- `delivery_price` — стоимость доставки

Если цена ещё не определена, оставьте `null`:
```json
"product_price": null
```

### Как добавить изображение товара

**Вариант 1: Через file_id**

1. Отправьте фото боту (или другому боту)
2. Скопируйте `file_id` из ответа
3. Добавьте в `data/products.json`:
```json
"image": "AgACAgIAAxkBAAIBZ2..."
```

**Вариант 2: Через URL**

```json
"image": "https://example.com/photo.jpg"
```

### Как использовать deep link для Instagram

Создайте ссылку вида:
```
https://t.me/BOT_USERNAME?start=instagram_table
```

Параметр после `start=` сохраняется как источник заявки.

Примеры источников:
- `instagram_table` — переход на журнальный столик
- `instagram_reels` — общий переход из Reels
- `telegram_post` — переход из Telegram-поста

## Как работать с базой данных

### Локальная SQLite

База данных находится в файле `data/bot.db`.

Для просмотра данных можно использовать:

```bash
# Установите sqlite3 (если не установлен)
brew install sqlite3  # macOS
sudo apt install sqlite3  # Linux

# Откройте базу данных
sqlite3 data/bot.db

# Просмотрите таблицы
sqlite> .tables

# Просмотрите заказы
sqlite> SELECT * FROM orders;

# Просмотрите вопросы
sqlite> SELECT * FROM questions;

# Выход
sqlite> .exit
```

### Структура таблицы orders

| Поле | Описание |
|------|----------|
| id | ID записи |
| order_number | Номер заявки (ORD-20260712-123456) |
| telegram_user_id | Telegram ID клиента |
| telegram_username | Username клиента |
| source | Источник перехода |
| product_name | Название товара |
| size | Выбранный размер |
| color | Выбранный цвет |
| city | Город доставки |
| customer_name | Имя клиента |
| contact | Контакт клиента |
| total_price | Итоговая стоимость |
| status | Статус заявки |
| created_at | Дата создания |

## Размещение на Railway

### Шаг 1: Подготовка репозитория

1. Создайте репозиторий на GitHub
2. Загрузите проект (без файла `.env`)
3. Добавьте `.env` в `.gitignore` если его там нет

### Шаг 2: Создание проекта на Railway

1. Зайдите на [railway.app](https://railway.app)
2. Нажмите **New Project** → **Deploy from GitHub repo**
3. Подключите свой репозиторий

### Шаг 3: Добавление PostgreSQL

1. В проекте нажмите **Add New** → **Database** → **PostgreSQL**
2. Railway автоматически создаст переменную `DATABASE_URL`

### Шаг 4: Добавление переменных окружения

В разделе **Variables** добавьте:

| Переменная | Значение |
|-----------|----------|
| BOT_TOKEN | Токен бота от BotFather |
| ADMIN_TELEGRAM_IDS | Ваш Telegram ID (число) |
| MANAGER_URL | Ссылка на менеджера |
| LOG_LEVEL | INFO |
| DATABASE_URL | Будет подставлен автоматически из PostgreSQL |

### Шаг 5: Деплой

1. Railway автоматически запустит деплой при пуше в main
2. После завершения в логах будет:
   ```
   Бот запускается...
   Бот готов к работе!
   ```

### Шаг 6: Проверка

1. Откройте бота в Telegram
2. Отправьте `/start`
3. Пройдите тестовое оформление заказа
4. Проверьте получение уведомления администратором

### Важно про Railway

- **Не загружайте `.env` в GitHub** — секреты добавляются только в Variables
- **SQLite без Volume теряет данные** при перезапуске — используйте PostgreSQL
- Бот работает как **worker-процесс** через long polling
- Railway автоматически перезапускает процесс при падении

## Конфигурация администраторов

Для получения уведомлений о новых заявках:

1. Узнайте свой Telegram ID (см. выше)
2. Добавьте его в `ADMIN_TELEGRAM_IDS` через запятую:

```env
ADMIN_TELEGRAM_IDS=123456789,987654321
```

## Структура проекта

```
telegram-furniture-bot/
├── app/
│   ├── main.py              # Точка входа
│   ├── config.py            # Конфигурация
│   ├── database/
│   │   ├── models.py        # Модели SQLAlchemy
│   │   ├── session.py       # Подключение к БД
│   │   └── repositories.py  # Работа с данными
│   ├── handlers/
│   │   ├── start.py         # Команды /start, /help
│   │   ├── catalog.py       # Каталог товаров
│   │   ├── order.py         # Оформление заказа (FSM)
│   │   ├── questions.py     # Вопросы клиентов
│   │   └── common.py        # Обработка ошибок
│   ├── keyboards/           # Inline-клавиатуры
│   ├── states/              # FSM-состояния
│   ├── services/            # Бизнес-логика
│   ├── texts/               # Тексты сообщений
│   └── utils/               # Утилиты
├── data/
│   └── products.json        # Каталог товаров
├── tests/                   # Тесты
├── .env.example             # Пример переменных
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── Procfile
├── railway.json
└── README.md
```

## Что является MVP

На первом этапе реализовано:
- ✅ Приветственное сообщение и главное меню
- ✅ Каталог с 4 товарами
- ✅ Карточки товаров с ценами
- ✅ Пошаговое оформление заказа (FSM)
- ✅ Выбор размера и цвета (когда применимо)
- ✅ Заказ товара по ссылке или фото
- ✅ Проверка и подтверждение заявки
- ✅ Сохранение в базу данных
- ✅ Уведомления администратору
- ✅ Вопросы от клиентов
- ✅ Deep links для Instagram
- ✅ Локальный запуск (SQLite)
- ✅ Размещение на Railway (PostgreSQL)
- ✅ Тесты

**Не реализовано в MVP:**
- Интеграция с платёжными системами
- Статусы заказов и трекинг
- Админ-панель
- Расчёт доставки по городам
- Система оплаты

## Решение проблем

### Бот не отвечает

1. Проверьте, что токен правильный
2. Проверьте, что бот запущен (нет ошибок в консоли)
3. Убедитесь, что токен актуален (можно перевыпустить в @BotFather)

### Ошибка подключения к базе данных

```bash
# Удалите старую базу и создайте заново
rm data/bot.db
python -m app.main
```

### Ошибка при запуске тестов

```bash
# Убедитесь, что зависимости установлены
pip install -r requirements.txt

# Запустите тесты
pytest -v
```

### Docker не запускается

```bash
# Пересоберите образ
docker-compose down
docker-compose build --no-cache
docker-compose up
```

## Лицензия

MIT
