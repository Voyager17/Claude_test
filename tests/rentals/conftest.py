import pytest
from fastapi.testclient import TestClient

from app.schemas.customer import CustomerRead
from app.schemas.movie import MovieRead
from app.schemas.rental import RentalCreate, RentalRead
from tests.urls import RentalURLs


@pytest.fixture
def created_rental(client: TestClient, created_customer: CustomerRead, created_movie: MovieRead) -> RentalRead:
    payload = RentalCreate.rand_init(customer_id=created_customer.id, movie_id=created_movie.id)
    response = client.post(RentalURLs.base, json=payload.model_dump())
    return RentalRead.model_validate(response.json())
