import httpx

from app.schemas.customer import CustomerRead
from tests.constants.constants import StatusCode
from tests.urls import CustomerURLs


class TestGetCustomer:
    def test_get_existing(self, client: httpx.Client, created_customer: CustomerRead):
        response = client.get(CustomerURLs.detail(created_customer.id))

        assert response.status_code == StatusCode.OK
        customer = CustomerRead.model_validate(response.json())
        assert customer.id == created_customer.id

    def test_get_not_found(self, client: httpx.Client):
        response = client.get(CustomerURLs.detail(9999))

        assert response.status_code == StatusCode.NOT_FOUND
        assert response.json()["detail"] == "Customer not found"
