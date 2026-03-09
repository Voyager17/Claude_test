import httpx

from app.schemas.movie import MovieRead
from tests.constants.constants import StatusCode
from tests.urls import MovieURLs


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
