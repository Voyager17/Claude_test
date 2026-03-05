from fastapi.testclient import TestClient

from app.schemas.customer import CustomerCreate, CustomerRead
from tests.constants.constants import StatusCode
from tests.db_queries import DBQueries
from tests.urls import CustomerURLs


class TestCreateCustomer:
    def test_success(self, client: TestClient, db_queries: DBQueries):
        payload = CustomerCreate.rand_init()
        response = client.post(CustomerURLs.base, json=payload.model_dump())

        assert response.status_code == StatusCode.CREATED
        customer = CustomerRead.model_validate(response.json())
        assert customer.full_name == payload.full_name
        assert customer.email == payload.email
        assert customer.is_active is True
        assert db_queries.count_customers() == 1

    def test_duplicate_email(self, client: TestClient, db_queries: DBQueries):
        payload = CustomerCreate.rand_init()
        client.post(CustomerURLs.base, json=payload.model_dump())
        response = client.post(CustomerURLs.base, json=payload.model_dump())

        assert response.status_code == StatusCode.CONFLICT
        assert response.json()["detail"] == "Email already registered"
        assert db_queries.count_customers() == 1

    def test_invalid_email(self, client: TestClient):
        payload = CustomerCreate.rand_init().model_dump()
        payload["email"] = "not-an-email"
        response = client.post(CustomerURLs.base, json=payload)

        assert response.status_code == StatusCode.UNPROCESSABLE_ENTITY

    def test_without_phone(self, client: TestClient):
        payload = CustomerCreate.rand_init().model_dump()
        payload.pop("phone")
        response = client.post(CustomerURLs.base, json=payload)

        assert response.status_code == StatusCode.CREATED
        customer = CustomerRead.model_validate(response.json())
        assert customer.phone is None

    def test_missing_required_fields(self, client: TestClient):
        response = client.post(CustomerURLs.base, json={})

        assert response.status_code == StatusCode.UNPROCESSABLE_ENTITY


class TestGetCustomer:
    def test_get_existing(self, client: TestClient, created_customer: CustomerRead):
        response = client.get(CustomerURLs.detail(created_customer.id))

        assert response.status_code == StatusCode.OK
        customer = CustomerRead.model_validate(response.json())
        assert customer.id == created_customer.id

    def test_get_not_found(self, client: TestClient):
        response = client.get(CustomerURLs.detail(9999))

        assert response.status_code == StatusCode.NOT_FOUND
        assert response.json()["detail"] == "Customer not found"


class TestListCustomers:
    def test_empty_list(self, client: TestClient):
        response = client.get(CustomerURLs.base)

        assert response.status_code == StatusCode.OK
        assert response.json() == []

    def test_returns_active_only(self, client: TestClient, created_customer: CustomerRead, db_queries: DBQueries):
        client.delete(CustomerURLs.detail(created_customer.id))
        response = client.get(CustomerURLs.base)

        assert response.status_code == StatusCode.OK
        assert response.json() == []
        assert db_queries.count_customers() == 1
        assert len(db_queries.select_active_customers()) == 0

    def test_pagination(self, client: TestClient):
        for _ in range(5):
            client.post(CustomerURLs.base, json=CustomerCreate.rand_init().model_dump())

        response = client.get(f"{CustomerURLs.base}?skip=1&limit=2")

        assert response.status_code == StatusCode.OK
        assert len(response.json()) == 2


class TestUpdateCustomer:
    def test_update_name(self, client: TestClient, created_customer: CustomerRead, db_queries: DBQueries):
        response = client.patch(CustomerURLs.detail(created_customer.id), json={"full_name": "Пётр Иванов"})

        assert response.status_code == StatusCode.OK
        customer = CustomerRead.model_validate(response.json())
        assert customer.full_name == "Пётр Иванов"
        assert db_queries.select_customer(created_customer.id).full_name == "Пётр Иванов"

    def test_update_not_found(self, client: TestClient):
        response = client.patch(CustomerURLs.detail(9999), json={"full_name": "X"})

        assert response.status_code == StatusCode.NOT_FOUND

    def test_update_invalid_email(self, client: TestClient, created_customer: CustomerRead):
        response = client.patch(CustomerURLs.detail(created_customer.id), json={"email": "bad-email"})

        assert response.status_code == StatusCode.UNPROCESSABLE_ENTITY


class TestDeleteCustomer:
    def test_soft_delete(self, client: TestClient, created_customer: CustomerRead, db_queries: DBQueries):
        response = client.delete(CustomerURLs.detail(created_customer.id))

        assert response.status_code == StatusCode.NO_CONTENT
        assert db_queries.select_customer(created_customer.id).is_active is False

    def test_delete_not_found(self, client: TestClient):
        response = client.delete(CustomerURLs.detail(9999))

        assert response.status_code == StatusCode.NOT_FOUND

    def test_deleted_not_in_list(self, client: TestClient, created_customer: CustomerRead, db_queries: DBQueries):
        client.delete(CustomerURLs.detail(created_customer.id))
        response = client.get(CustomerURLs.base)

        assert created_customer.id not in {c["id"] for c in response.json()}
        assert len(db_queries.select_active_customers()) == 0
