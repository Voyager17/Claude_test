import httpx

from app.schemas.movie import MovieCreate, MovieRead
from tests.constants.constants import StatusCode
from tests.urls import MovieURLs


class TestCreateMovie:
    def test_success(self, client: httpx.Client, db_cleanup: list):
        payload = MovieCreate.rand_init()
        payload.rental_price_per_day = 0
        response = client.post(MovieURLs.base, json=payload.model_dump())

        assert response.status_code == StatusCode.CREATED
        movie = MovieRead.model_validate(response.json())
        db_cleanup.append(("movies", movie.id))
        assert movie.title == payload.title
        assert movie.director == payload.director
        assert movie.year == payload.year
        assert movie.is_active is True

    def test_invalid_year(self, client: httpx.Client):
        payload = MovieCreate.rand_init()
        payload.year = 1800
        response = client.post(MovieURLs.base, json=payload.model_dump())

        assert response.status_code == StatusCode.UNPROCESSABLE_ENTITY

    def test_invalid_rating(self, client: httpx.Client):
        payload = MovieCreate.rand_init().model_dump()
        payload["rating"] = 11.0
        response = client.post(MovieURLs.base, json=payload)

        assert response.status_code == StatusCode.UNPROCESSABLE_ENTITY

    def test_zero_price(self, client: httpx.Client):
        payload = MovieCreate.rand_init().model_dump()
        payload["rental_price_per_day"] = 0
        response = client.post(MovieURLs.base, json=payload)

        assert response.status_code == StatusCode.UNPROCESSABLE_ENTITY

    def test_missing_required_fields(self, client: httpx.Client):
        response = client.post(MovieURLs.base, json={})

        assert response.status_code == StatusCode.UNPROCESSABLE_ENTITY


class TestGetMovie:
    def test_get_existing(self, client: httpx.Client, created_movie: MovieRead):
        response = client.get(MovieURLs.detail(created_movie.id))

        assert response.status_code == StatusCode.OK
        movie = MovieRead.model_validate(response.json())
        assert movie.id == created_movie.id

    def test_get_not_found(self, client: httpx.Client):
        response = client.get(MovieURLs.detail(9999))

        assert response.status_code == StatusCode.NOT_FOUND
        assert response.json()["detail"] == "Movie not found"


class TestListMovies:
    def test_returns_active_only(self, client: httpx.Client, created_movie: MovieRead):
        client.delete(MovieURLs.detail(created_movie.id))
        response = client.get(MovieURLs.base)

        assert response.status_code == StatusCode.OK
        returned_ids = {m["id"] for m in response.json()}
        assert created_movie.id not in returned_ids
        assert client.get(MovieURLs.detail(created_movie.id)).json()["is_active"] is False

    def test_pagination(self, client: httpx.Client, db_cleanup: list):
        for _ in range(5):
            response = client.post(MovieURLs.base, json=MovieCreate.rand_init().model_dump())
            db_cleanup.append(("movies", response.json()["id"]))

        response = client.get(f"{MovieURLs.base}?skip=2&limit=2")

        assert response.status_code == StatusCode.OK
        assert len(response.json()) == 2


class TestUpdateMovie:
    def test_update_title(self, client: httpx.Client, created_movie: MovieRead):
        response = client.patch(MovieURLs.detail(created_movie.id), json={"title": "New Title"})

        assert response.status_code == StatusCode.OK
        movie = MovieRead.model_validate(response.json())
        assert movie.title == "New Title"

    def test_update_not_found(self, client: httpx.Client):
        response = client.patch(MovieURLs.detail(9999), json={"title": "X"})

        assert response.status_code == StatusCode.NOT_FOUND

    def test_update_invalid_rating(self, client: httpx.Client, created_movie: MovieRead):
        response = client.patch(MovieURLs.detail(created_movie.id), json={"rating": -1.0})

        assert response.status_code == StatusCode.UNPROCESSABLE_ENTITY


class TestDeleteMovie:
    def test_soft_delete(self, client: httpx.Client, created_movie: MovieRead):
        response = client.delete(MovieURLs.detail(created_movie.id))

        assert response.status_code == StatusCode.NO_CONTENT
        assert client.get(MovieURLs.detail(created_movie.id)).json()["is_active"] is False

    def test_delete_not_found(self, client: httpx.Client):
        response = client.delete(MovieURLs.detail(9999))

        assert response.status_code == StatusCode.NOT_FOUND

    def test_deleted_not_in_list(self, client: httpx.Client, created_movie: MovieRead):
        client.delete(MovieURLs.detail(created_movie.id))
        response = client.get(MovieURLs.base)

        assert created_movie.id not in {m["id"] for m in response.json()}
