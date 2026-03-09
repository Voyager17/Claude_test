import httpx

from app.schemas.movie import MovieCreate, MovieRead
from tests.constants.constants import StatusCode
from tests.urls import MovieURLs


class TestCreateMovie:
    def test_success(self, client: httpx.Client, db_cleanup: list):
        payload = MovieCreate.rand_init()
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
