import httpx

from app.schemas.customer import CustomerCreate, CustomerRead
from tests.constants.constants import StatusCode
from tests.urls import CustomerURLs


class TestCreateCustomer:
    def test_success(self, client: httpx.Client, db_cleanup: list):
        payload = CustomerCreate.rand_init()
        response = client.post(CustomerURLs.base, json=payload.model_dump())

        assert response.status_code == StatusCode.CREATED
        customer = CustomerRead.model_validate(response.json())
        db_cleanup.append(("customers", customer.id))
        assert customer.full_name == payload.full_name
        assert customer.email == payload.email
        assert customer.is_active is True

    def test_duplicate_email(self, client: httpx.Client, db_cleanup: list):
        payload = CustomerCreate.rand_init()
        r1 = client.post(CustomerURLs.base, json=payload.model_dump())
        db_cleanup.append(("customers", r1.json()["id"]))
        response = client.post(CustomerURLs.base, json=payload.model_dump())

        assert response.status_code == StatusCode.CONFLICT
        assert response.json()["detail"] == "Email already registered"

    def test_invalid_email(self, client: httpx.Client):
        payload = CustomerCreate.rand_init().model_dump()
        payload["email"] = "not-an-email"
        response = client.post(CustomerURLs.base, json=payload)

        assert response.status_code == StatusCode.UNPROCESSABLE_ENTITY

    def test_without_phone(self, client: httpx.Client, db_cleanup: list):
        payload = CustomerCreate.rand_init().model_dump()
        payload.pop("phone")
        response = client.post(CustomerURLs.base, json=payload)

        assert response.status_code == StatusCode.CREATED
        customer = CustomerRead.model_validate(response.json())
        db_cleanup.append(("customers", customer.id))
        assert customer.phone is None

    def test_missing_required_fields(self, client: httpx.Client):
        response = client.post(CustomerURLs.base, json={})

        assert response.status_code == StatusCode.UNPROCESSABLE_ENTITY
