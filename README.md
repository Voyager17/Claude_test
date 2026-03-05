# Video Rental Store API

REST API для управления прокатом видеофильмов. Позволяет вести каталог фильмов, базу клиентов и учёт аренд.

## Стек

- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2** — ORM
- **SQLite** — база данных (для разработки)
- **Pydantic v2** — валидация данных
- **uv** — менеджер пакетов и виртуальных окружений
- **Alembic** — миграции БД

## Быстрый старт

```bash
# Установить зависимости
uv sync --all-extras

# Запустить сервер
uv run uvicorn app.main:app --reload
```

API будет доступно на `http://localhost:8000`.
Swagger UI: `http://localhost:8000/docs`

## Структура проекта

```
d:/ai/
├── app/
│   ├── main.py               # Точка входа, инициализация приложения
│   ├── core/
│   │   ├── config.py         # Настройки приложения
│   │   └── database.py       # Подключение к БД
│   ├── models/               # ORM-модели таблиц
│   │   ├── movie.py
│   │   ├── customer.py
│   │   └── rental.py
│   ├── schemas/              # Pydantic-схемы запросов и ответов
│   │   ├── movie.py
│   │   ├── customer.py
│   │   └── rental.py
│   └── api/v1/
│       ├── router.py         # Главный роутер API
│       └── endpoints/
│           ├── movies.py     # CRUD фильмов
│           ├── customers.py  # CRUD клиентов
│           └── rentals.py    # Аренда и возврат
├── scripts/
│   └── seed.py               # Заполнение БД тестовыми данными
├── tests/
├── pyproject.toml
└── .env                      # Переменные окружения (не в git)
```

## API

Все эндпоинты доступны по префиксу `/api/v1/`.

### Фильмы `/api/v1/movies`

| Метод  | Путь           | Описание                        |
|--------|----------------|---------------------------------|
| GET    | `/`            | Список всех активных фильмов    |
| GET    | `/{id}`        | Получить фильм по ID            |
| POST   | `/`            | Добавить фильм                  |
| PATCH  | `/{id}`        | Обновить данные фильма          |
| DELETE | `/{id}`        | Деактивировать фильм (soft delete) |

**Пример создания фильма:**
```json
POST /api/v1/movies
{
  "title": "Inception",
  "director": "Christopher Nolan",
  "year": 2010,
  "genre": "Sci-Fi",
  "rating": 8.8,
  "rental_price_per_day": 2.99,
  "available_copies": 4
}
```

### Клиенты `/api/v1/customers`

| Метод  | Путь    | Описание                           |
|--------|---------|------------------------------------|
| GET    | `/`     | Список активных клиентов           |
| GET    | `/{id}` | Получить клиента по ID             |
| POST   | `/`     | Зарегистрировать клиента           |
| PATCH  | `/{id}` | Обновить данные клиента            |
| DELETE | `/{id}` | Деактивировать клиента (soft delete) |

**Пример создания клиента:**
```json
POST /api/v1/customers
{
  "full_name": "Иван Петров",
  "email": "ivan@example.com",
  "phone": "+7-916-123-45-67"
}
```

### Аренды `/api/v1/rentals`

| Метод | Путь                | Описание                      |
|-------|---------------------|-------------------------------|
| GET   | `/`                 | Список всех аренд             |
| GET   | `/{id}`             | Получить аренду по ID         |
| POST  | `/`                 | Создать аренду                |
| POST  | `/{id}/return`      | Зафиксировать возврат фильма  |

**Пример создания аренды:**
```json
POST /api/v1/rentals
{
  "customer_id": 1,
  "movie_id": 3,
  "rental_days": 5
}
```

При создании аренды автоматически:
- Рассчитывается стоимость: `rental_price_per_day × rental_days`
- Устанавливается `due_date`
- Уменьшается `available_copies` у фильма

При возврате (`POST /{id}/return`):
- Фиксируется `returned_at`
- Увеличивается `available_copies` у фильма

## Конфигурация

Создайте файл `.env` в корне проекта:

```env
DATABASE_URL=sqlite:///./rental.db
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

## Тестовые данные

```bash
uv run python scripts/seed.py
```

Добавляет 10 фильмов, 5 клиентов и 6 аренд (3 активных, 3 завершённых).

## Разработка

```bash
# Линтинг
uv run ruff check .

# Форматирование
uv run ruff format .

# Тесты
uv run pytest
```
