import httpx

from app.schemas.movie import MovieRead
from tests.constants.constants import StatusCode
from tests.urls import MovieURLs


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
