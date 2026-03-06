from typing import Iterator

import pytest
import httpx
from sqlalchemy import text

from app.schemas.customer import CustomerRead
from app.schemas.movie import MovieRead
from app.schemas.rental import RentalCreate, RentalRead
from tests.conftest import TestingSessionLocal
from tests.urls import RentalURLs


@pytest.fixture
def created_rental(client: httpx.Client, created_customer: CustomerRead, created_movie: MovieRead) -> Iterator[RentalRead]:
    payload = RentalCreate.rand_init(
        customer_id=created_customer.id, movie_id=created_movie.id)
    response = client.post(RentalURLs.base, json=payload.model_dump())
    rental = RentalRead.model_validate(response.json())
    yield rental
    session = TestingSessionLocal()
    try:
        session.execute(text("DELETE FROM rentals WHERE id = :id"), {
                        "id": rental.id})
        session.commit()
    finally:
        session.close()
