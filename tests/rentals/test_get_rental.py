import httpx

from app.schemas.rental import RentalRead
from tests.constants.constants import StatusCode
from tests.urls import RentalURLs


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
