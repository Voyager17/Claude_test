import httpx

from app.schemas.rental import RentalRead
from tests.constants.constants import StatusCode
from tests.urls import RentalURLs


class TestListRentals:
    def test_created_rental_in_list(self, client: httpx.Client, created_rental: RentalRead):
        rentals = [RentalRead.model_validate(r) for r in client.get(RentalURLs.base).json()]

        assert any(r.id == created_rental.id for r in rentals)

    def test_list_status_ok(self, client: httpx.Client):
        response = client.get(RentalURLs.base)

        assert response.status_code == StatusCode.OK
