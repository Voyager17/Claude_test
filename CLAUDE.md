# CLAUDE.md

## Project overview

FastAPI REST API for a video rental store. SQLite for development, SQLAlchemy ORM, Pydantic v2 schemas.

## Commands

```bash
# Run dev server
uv run uvicorn app.main:app --reload

# Install dependencies (including dev)
uv sync --all-extras

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Tests
uv run pytest

# Seed database with sample data
uv run python scripts/seed.py
```

## Architecture

```
app/
├── main.py              # FastAPI app, DB init, router mount
├── core/
│   ├── config.py        # Settings via pydantic-settings (.env support)
│   └── database.py      # SQLAlchemy engine, SessionLocal, Base, get_db()
├── models/              # SQLAlchemy ORM models (Movie, Customer, Rental)
├── schemas/             # Pydantic v2 schemas (Create / Update / Read)
└── api/v1/
    ├── router.py        # Aggregates all endpoint routers
    └── endpoints/       # movies.py, customers.py, rentals.py
```

## Key conventions

- All endpoints are versioned under `/api/v1/`
- Soft delete: `is_active = False` instead of real DELETE for movies and customers
- `get_db()` is a FastAPI dependency injecting a SQLAlchemy session per request
- Schemas use `model_config = {"from_attributes": True}` for ORM compatibility
- `available_copies` on Movie is decremented on rental creation and incremented on return

## Environment variables

Create `.env` in project root to override defaults:

```
DATABASE_URL=sqlite:///./rental.db
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=10080
```

## Database

SQLite file `rental.db` is created automatically on first startup via `Base.metadata.create_all()`.
Add `rental.db` to `.gitignore` — it is already there.
