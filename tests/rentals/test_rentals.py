import pytest
import httpx

from app.schemas.customer import CustomerRead
from app.schemas.movie import MovieRead
from app.schemas.rental import RentalCreate, RentalRead
from tests.constants.constants import StatusCode
from tests.urls import CustomerURLs, MovieURLs, RentalURLs


class TestCreateRental:
    def test_success(
        self, client: httpx.Client, created_customer: CustomerRead, created_movie: MovieRead,
    ):
        payload = RentalCreate.rand_init(customer_id=created_customer.id, movie_id=created_movie.id)
        response = client.post(RentalURLs.base, json=payload.model_dump())

        assert response.status_code == StatusCode.CREATED
        rental = RentalRead.model_validate(response.json())
        assert rental.customer_id == created_customer.id
        assert rental.movie_id == created_movie.id
        assert rental.is_returned is False
        assert rental.returned_at is None

    def test_price_calculated_correctly(
        self, client: httpx.Client, created_customer: CustomerRead, created_movie: MovieRead,
    ):
        payload = RentalCreate.rand_init(customer_id=created_customer.id, movie_id=created_movie.id)
        response = client.post(RentalURLs.base, json=payload.model_dump())

        rental = RentalRead.model_validate(response.json())
        expected = created_movie.rental_price_per_day * payload.rental_days
        assert rental.total_price == pytest.approx(expected)

    def test_copies_decremented(
        self, client: httpx.Client, created_customer: CustomerRead, created_movie: MovieRead,
    ):
        payload = RentalCreate.rand_init(customer_id=created_customer.id, movie_id=created_movie.id)
        client.post(RentalURLs.base, json=payload.model_dump())

        movie_after = client.get(MovieURLs.detail(created_movie.id)).json()
        assert movie_after["available_copies"] == created_movie.available_copies - 1

    def test_no_copies_available(
        self, client: httpx.Client, created_customer: CustomerRead, created_movie: MovieRead,
    ):
        payload = RentalCreate.rand_init(customer_id=created_customer.id, movie_id=created_movie.id)
        for _ in range(created_movie.available_copies):
            client.post(RentalURLs.base, json=payload.model_dump())

        response = client.post(RentalURLs.base, json=payload.model_dump())

        assert response.status_code == StatusCode.CONFLICT
        assert response.json()["detail"] == "No copies available"

    def test_customer_not_found(self, client: httpx.Client, created_movie: MovieRead):
        payload = RentalCreate.rand_init(customer_id=9999, movie_id=created_movie.id)
        response = client.post(RentalURLs.base, json=payload.model_dump())

        assert response.status_code == StatusCode.NOT_FOUND
        assert response.json()["detail"] == "Customer not found"

    def test_movie_not_found(self, client: httpx.Client, created_customer: CustomerRead):
        payload = RentalCreate.rand_init(customer_id=created_customer.id, movie_id=9999)
        response = client.post(RentalURLs.base, json=payload.model_dump())

        assert response.status_code == StatusCode.NOT_FOUND
        assert response.json()["detail"] == "Movie not found"

    def test_inactive_customer_not_allowed(
        self, client: httpx.Client, created_customer: CustomerRead, created_movie: MovieRead,
    ):
        client.delete(CustomerURLs.detail(created_customer.id))
        payload = RentalCreate.rand_init(customer_id=created_customer.id, movie_id=created_movie.id)
        response = client.post(RentalURLs.base, json=payload.model_dump())

        assert response.status_code == StatusCode.NOT_FOUND

    def test_inactive_movie_not_allowed(
        self, client: httpx.Client, created_customer: CustomerRead, created_movie: MovieRead,
    ):
        client.delete(MovieURLs.detail(created_movie.id))
        payload = RentalCreate.rand_init(customer_id=created_customer.id, movie_id=created_movie.id)
        response = client.post(RentalURLs.base, json=payload.model_dump())

        assert response.status_code == StatusCode.NOT_FOUND

    def test_invalid_rental_days(
        self, client: httpx.Client, created_customer: CustomerRead, created_movie: MovieRead,
    ):
        payload = RentalCreate.rand_init(customer_id=created_customer.id, movie_id=created_movie.id).model_dump()
        payload["rental_days"] = 0
        response = client.post(RentalURLs.base, json=payload)

        assert response.status_code == StatusCode.UNPROCESSABLE_ENTITY


class TestGetRental:
    def test_get_existing(self, client: httpx.Client, created_rental: RentalRead):
        response = client.get(RentalURLs.detail(created_rental.id))

        assert response.status_code == StatusCode.OK
        rental = RentalRead.model_validate(response.json())
        assert rental.id == created_rental.id

    def test_get_not_found(self, client: httpx.Client):
        response = client.get(RentalURLs.detail(9999))

        assert response.status_code == StatusCode.NOT_FOUND
        assert response.json()["detail"] == "Rental not found"


class TestListRentals:
    def test_created_rental_in_list(self, client: httpx.Client, created_rental: RentalRead):
        rentals = [RentalRead.model_validate(r) for r in client.get(RentalURLs.base).json()]

        assert any(r.id == created_rental.id for r in rentals)

    def test_list_status_ok(self, client: httpx.Client):
        response = client.get(RentalURLs.base)

        assert response.status_code == StatusCode.OK


class TestReturnRental:
    def test_success(
        self, client: httpx.Client, created_rental: RentalRead, created_movie: MovieRead,
    ):
        copies_before = client.get(MovieURLs.detail(created_movie.id)).json()["available_copies"]
        response = client.post(RentalURLs.return_(created_rental.id))

        assert response.status_code == StatusCode.OK
        rental = RentalRead.model_validate(response.json())
        assert rental.is_returned is True
        assert rental.returned_at is not None
        copies_after = client.get(MovieURLs.detail(created_movie.id)).json()["available_copies"]
        assert copies_after == copies_before + 1

    def test_already_returned(self, client: httpx.Client, created_rental: RentalRead):
        client.post(RentalURLs.return_(created_rental.id))
        response = client.post(RentalURLs.return_(created_rental.id))

        assert response.status_code == StatusCode.CONFLICT
        assert response.json()["detail"] == "Already returned"

    def test_return_not_found(self, client: httpx.Client):
        response = client.post(RentalURLs.return_(9999))

        assert response.status_code == StatusCode.NOT_FOUND
