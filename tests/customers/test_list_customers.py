import httpx

from app.schemas.customer import CustomerCreate, CustomerRead
from tests.constants.constants import StatusCode
from tests.urls import CustomerURLs


class TestListCustomers:
    def test_returns_active_only(self, client: httpx.Client, created_customer: CustomerRead):
        client.delete(CustomerURLs.detail(created_customer.id))
        response = client.get(CustomerURLs.base)

        assert response.status_code == StatusCode.OK
        returned_ids = {c["id"] for c in response.json()}
        assert created_customer.id not in returned_ids
        assert client.get(CustomerURLs.detail(created_customer.id)).json()["is_active"] is False

    def test_pagination(self, client: httpx.Client, db_cleanup: list):
        for _ in range(5):
            response = client.post(CustomerURLs.base, json=CustomerCreate.rand_init().model_dump())
            db_cleanup.append(("customers", response.json()["id"]))

        response = client.get(f"{CustomerURLs.base}?skip=1&limit=2")

        assert response.status_code == StatusCode.OK
        assert len(response.json()) == 2
