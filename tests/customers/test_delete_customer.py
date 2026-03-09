import httpx

from app.schemas.customer import CustomerRead
from tests.constants.constants import StatusCode
from tests.urls import CustomerURLs


class TestDeleteCustomer:
    def test_soft_delete(self, client: httpx.Client, created_customer: CustomerRead):
        response = client.delete(CustomerURLs.detail(created_customer.id))

        assert response.status_code == StatusCode.NO_CONTENT
        assert client.get(CustomerURLs.detail(created_customer.id)).json()["is_active"] is False

    def test_delete_not_found(self, client: httpx.Client):
        response = client.delete(CustomerURLs.detail(10_000_000))

        assert response.status_code == StatusCode.NOT_FOUND

    def test_deleted_not_in_list(self, client: httpx.Client, created_customer: CustomerRead):
        client.delete(CustomerURLs.detail(created_customer.id))
        response = client.get(CustomerURLs.base)

        assert created_customer.id not in {c["id"] for c in response.json()}
