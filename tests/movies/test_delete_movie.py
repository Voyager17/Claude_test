import httpx

from app.schemas.movie import MovieRead
from tests.constants.constants import StatusCode
from tests.urls import MovieURLs


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
