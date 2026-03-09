import httpx

from app.schemas.movie import MovieCreate, MovieRead
from tests.constants.constants import StatusCode
from tests.urls import MovieURLs


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
