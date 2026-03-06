# База данных — инструкция

## Как всё устроено

Проект запускается через Docker Compose. Два контейнера:

- **postgres** — PostgreSQL 16, хранит все данные
- **api** — FastAPI приложение, подключается к postgres внутри Docker-сети

Тесты запускаются **не в Docker** — с твоей машины. Они подключаются к тому же postgres через проброшенный порт `5432`.

```
Твоя машина
├── uv run pytest  ──────────────────────────────┐
│                                                 │
└── Docker Compose                                │
    ├── api (порт 8001) ──→ postgres (внутри)     │
    └── postgres (порт 5432) ←───────────────────┘
```

---

## Запуск

```bash
# Запустить postgres + api
docker compose up -d

# Проверить что оба контейнера работают
docker compose ps

# Остановить
docker compose down
```

После первого `docker compose up` FastAPI автоматически создаёт все таблицы в postgres (через `Base.metadata.create_all` в `app/main.py`).

---

## Подключение к базе данных

### Через psql в терминале

```bash
docker compose exec postgres psql -U rental -d rental
```

Полезные команды внутри psql:
```sql
\dt                    -- список таблиц
\d movies              -- структура таблицы movies
SELECT * FROM movies;  -- посмотреть все фильмы
\q                     -- выйти
```

### Через любой GUI клиент (DBeaver, DataGrip, TablePlus)

| Параметр | Значение |
|----------|----------|
| Host     | localhost |
| Port     | 5432 |
| Database | rental |
| User     | rental |
| Password | rental |

---

## Структура таблиц

### movies
| Колонка | Тип | Описание |
|---------|-----|----------|
| id | integer | первичный ключ |
| title | varchar | название фильма |
| director | varchar | режиссёр |
| year | integer | год выпуска |
| genre | varchar | жанр |
| rating | float | рейтинг (0–10) |
| rental_price_per_day | float | цена аренды за день |
| available_copies | integer | количество доступных копий |
| is_active | boolean | `true` = активен, `false` = мягко удалён |

### customers
| Колонка | Тип | Описание |
|---------|-----|----------|
| id | integer | первичный ключ |
| full_name | varchar | полное имя |
| email | varchar | email (уникальный) |
| phone | varchar | телефон (необязательный) |
| is_active | boolean | `true` = активен, `false` = мягко удалён |

### rentals
| Колонка | Тип | Описание |
|---------|-----|----------|
| id | integer | первичный ключ |
| customer_id | integer | FK → customers.id |
| movie_id | integer | FK → movies.id |
| rented_at | timestamp | дата и время аренды |
| due_date | timestamp | когда нужно вернуть |
| total_price | float | итоговая цена |
| is_returned | boolean | возвращён ли фильм |
| returned_at | timestamp | дата и время возврата (NULL если не возвращён) |

---

## Мягкое удаление (soft delete)

Фильмы и клиенты **не удаляются физически**. При DELETE-запросе через API выставляется `is_active = false`.

```sql
-- Список активных фильмов (что видит API)
SELECT * FROM movies WHERE is_active = true;

-- Все фильмы включая удалённые
SELECT * FROM movies;

-- Посмотреть удалённых клиентов
SELECT * FROM customers WHERE is_active = false;
```

Получить конкретный фильм/клиента по ID через API можно даже после удаления — эндпоинт GET /{id} не фильтрует по `is_active`.

---

## Как работают тесты с базой

Тесты делают **реальные HTTP-запросы** к API на `http://localhost:8001`.

**Изоляция данных**: каждый тест убирает за собой созданные записи через прямые DELETE-запросы в postgres.

```
Тест создаёт фильм через POST /api/v1/movies
    → yield (тест выполняется)
    → DELETE FROM rentals WHERE movie_id = ?
    → DELETE FROM movies WHERE id = ?
```

Фикстуры в `tests/conftest.py`:
- `created_movie` — создаёт фильм, удаляет после теста
- `created_customer` — создаёт клиента, удаляет после теста
- `db_cleanup` — список `(table, id)` для ручной регистрации записей в тестах

Фикстура `db_queries` в `tests/db_queries.py` даёт прямой доступ к postgres из тестов (без HTTP).

---

## Данные между запусками

Данные **сохраняются** между `docker compose down` и `docker compose up` — хранятся в Docker volume `postgres_data`.

```bash
# Полностью удалить все данные (сбросить базу)
docker compose down -v

# После этого docker compose up создаст пустую БД заново
docker compose up -d
```
