from typing import Iterator

import pytest
import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.schemas.customer import CustomerCreate, CustomerRead
from app.schemas.movie import MovieCreate, MovieRead
from tests.db_queries import DBQueries
from tests.urls import CustomerURLs, MovieURLs

BASE_URL = "http://localhost:8001"

engine = create_engine("postgresql://rental:rental@localhost:5432/rental")
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _hard_delete(statements: list[tuple[str, dict]]) -> None:
    session = TestingSessionLocal()
    try:
        for sql, params in statements:
            session.execute(text(sql), params)
        session.commit()
    finally:
        session.close()


@pytest.fixture
def client() -> Iterator[httpx.Client]:
    with httpx.Client(base_url=BASE_URL) as c:
        yield c


@pytest.fixture
def db_queries() -> Iterator[DBQueries]:
    q = DBQueries(TestingSessionLocal)
    yield q
    q.close()


@pytest.fixture
def db_cleanup() -> Iterator[list[tuple[str, int]]]:
    """Register (table, id) tuples; hard-deleted after test in reverse order."""
    to_delete: list[tuple[str, int]] = []
    yield to_delete
    _hard_delete([
        (f"DELETE FROM {table} WHERE id = :id", {"id": id_})
        for table, id_ in reversed(to_delete)
    ])


@pytest.fixture
def created_movie(client: httpx.Client) -> Iterator[MovieRead]:
    payload = MovieCreate.rand_init()
    response = client.post(MovieURLs.base, json=payload.model_dump())
    movie = MovieRead.model_validate(response.json())
    yield movie
    _hard_delete([
        ("DELETE FROM rentals WHERE movie_id = :id", {"id": movie.id}),
        ("DELETE FROM movies WHERE id = :id", {"id": movie.id}),
    ])


@pytest.fixture
def created_customer(client: httpx.Client) -> Iterator[CustomerRead]:
    payload = CustomerCreate.rand_init()
    response = client.post(CustomerURLs.base, json=payload.model_dump())
    customer = CustomerRead.model_validate(response.json())
    yield customer
    _hard_delete([
        ("DELETE FROM rentals WHERE customer_id = :id", {"id": customer.id}),
        ("DELETE FROM customers WHERE id = :id", {"id": customer.id}),
    ])
