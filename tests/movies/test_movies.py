from fastapi.testclient import TestClient

from app.schemas.movie import MovieCreate, MovieRead
from tests.constants.constants import StatusCode
from tests.db_queries import DBQueries
from tests.urls import MovieURLs


class TestCreateMovie:
    def test_success(self, client: TestClient, db_queries: DBQueries):
        payload = MovieCreate.rand_init()
        response = client.post(MovieURLs.base, json=payload.model_dump())

        assert response.status_code == StatusCode.CREATED
        movie = MovieRead.model_validate(response.json())
        assert movie.title == payload.title
        assert movie.director == payload.director
        assert movie.year == payload.year
        assert movie.is_active is True
        assert db_queries.count_movies() == 1

    def test_invalid_year(self, client: TestClient, db_queries: DBQueries):
        payload = MovieCreate.rand_init()
        payload.year = 1800
        response = client.post(MovieURLs.base, json=payload.model_dump())

        assert response.status_code == StatusCode.UNPROCESSABLE_ENTITY
        assert db_queries.count_movies() == 0

    def test_invalid_rating(self, client: TestClient):
        payload = MovieCreate.rand_init().model_dump()
        payload["rating"] = 11.0
        response = client.post(MovieURLs.base, json=payload)

        assert response.status_code == StatusCode.UNPROCESSABLE_ENTITY

    def test_zero_price(self, client: TestClient):
        payload = MovieCreate.rand_init().model_dump()
        payload["rental_price_per_day"] = 0
        response = client.post(MovieURLs.base, json=payload)

        assert response.status_code == StatusCode.UNPROCESSABLE_ENTITY

    def test_missing_required_fields(self, client: TestClient):
        response = client.post(MovieURLs.base, json={})

        assert response.status_code == StatusCode.UNPROCESSABLE_ENTITY


class TestGetMovie:
    def test_get_existing(self, client: TestClient, created_movie: MovieRead):
        response = client.get(MovieURLs.detail(created_movie.id))

        assert response.status_code == StatusCode.OK
        movie = MovieRead.model_validate(response.json())
        assert movie.id == created_movie.id

    def test_get_not_found(self, client: TestClient):
        response = client.get(MovieURLs.detail(9999))

        assert response.status_code == StatusCode.NOT_FOUND
        assert response.json()["detail"] == "Movie not found"


class TestListMovies:
    def test_empty_list(self, client: TestClient):
        response = client.get(MovieURLs.base)

        assert response.status_code == StatusCode.OK
        assert response.json() == []

    def test_returns_active_only(self, client: TestClient, created_movie: MovieRead, db_queries: DBQueries):
        client.delete(MovieURLs.detail(created_movie.id))
        response = client.get(MovieURLs.base)

        assert response.status_code == StatusCode.OK
        assert response.json() == []
        assert db_queries.count_movies() == 1
        assert db_queries.count_active_movies() == 0

    def test_pagination(self, client: TestClient):
        for _ in range(5):
            client.post(MovieURLs.base, json=MovieCreate.rand_init().model_dump())

        response = client.get(f"{MovieURLs.base}?skip=2&limit=2")

        assert response.status_code == StatusCode.OK
        assert len(response.json()) == 2


class TestUpdateMovie:
    def test_update_title(self, client: TestClient, created_movie: MovieRead, db_queries: DBQueries):
        response = client.patch(MovieURLs.detail(created_movie.id), json={"title": "New Title"})

        assert response.status_code == StatusCode.OK
        movie = MovieRead.model_validate(response.json())
        assert movie.title == "New Title"
        assert db_queries.select_movie(created_movie.id).title == "New Title"

    def test_update_not_found(self, client: TestClient):
        response = client.patch(MovieURLs.detail(9999), json={"title": "X"})

        assert response.status_code == StatusCode.NOT_FOUND

    def test_update_invalid_rating(self, client: TestClient, created_movie: MovieRead):
        response = client.patch(MovieURLs.detail(created_movie.id), json={"rating": -1.0})

        assert response.status_code == StatusCode.UNPROCESSABLE_ENTITY


class TestDeleteMovie:
    def test_soft_delete(self, client: TestClient, created_movie: MovieRead, db_queries: DBQueries):
        response = client.delete(MovieURLs.detail(created_movie.id))

        assert response.status_code == StatusCode.NO_CONTENT
        assert db_queries.select_movie(created_movie.id).is_active is False

    def test_delete_not_found(self, client: TestClient):
        response = client.delete(MovieURLs.detail(9999))

        assert response.status_code == StatusCode.NOT_FOUND

    def test_deleted_not_in_list(self, client: TestClient, created_movie: MovieRead, db_queries: DBQueries):
        client.delete(MovieURLs.detail(created_movie.id))
        response = client.get(MovieURLs.base)

        assert created_movie.id not in {m["id"] for m in response.json()}
        assert db_queries.count_active_movies() == 0
