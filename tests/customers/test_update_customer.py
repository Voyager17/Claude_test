import httpx

from app.schemas.customer import CustomerRead
from tests.constants.constants import StatusCode
from tests.urls import CustomerURLs


class TestUpdateCustomer:
    def test_update_name(self, client: httpx.Client, created_customer: CustomerRead):
        response = client.patch(CustomerURLs.detail(created_customer.id), json={"full_name": "Пётр Иванов"})

        assert response.status_code == StatusCode.OK
        customer = CustomerRead.model_validate(response.json())
        assert customer.full_name == "Пётр Иванов"

    def test_update_not_found(self, client: httpx.Client):
        response = client.patch(CustomerURLs.detail(9999), json={"full_name": "X"})

        assert response.status_code == StatusCode.NOT_FOUND

    def test_update_invalid_email(self, client: httpx.Client, created_customer: CustomerRead):
        response = client.patch(CustomerURLs.detail(created_customer.id), json={"email": "bad-email"})

        assert response.status_code == StatusCode.UNPROCESSABLE_ENTITY
