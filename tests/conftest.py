import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app
from app.schemas.customer import CustomerCreate, CustomerRead
from app.schemas.movie import MovieCreate, MovieRead
from tests.db_queries import DBQueries
from tests.urls import CustomerURLs, MovieURLs

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def created_movie(client: TestClient) -> MovieRead:
    payload = MovieCreate.rand_init()
    response = client.post(MovieURLs.base, json=payload.model_dump())
    return MovieRead.model_validate(response.json())


@pytest.fixture
def created_customer(client: TestClient) -> CustomerRead:
    payload = CustomerCreate.rand_init()
    response = client.post(CustomerURLs.base, json=payload.model_dump())
    return CustomerRead.model_validate(response.json())


@pytest.fixture
def db_queries(db) -> DBQueries:
    return DBQueries(db)
