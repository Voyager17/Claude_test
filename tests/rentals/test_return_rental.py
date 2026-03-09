import httpx

from app.schemas.movie import MovieRead
from app.schemas.rental import RentalRead
from tests.constants.constants import StatusCode
from tests.urls import MovieURLs, RentalURLs


class TestReturnRental:
    def test_success(
        self, client: httpx.Client, created_rental: RentalRead, created_movie: MovieRead,
    ):
        copies_before = client.get(MovieURLs.detail(created_movie.id)).json()["available_copies"]
        response = client.post(RentalURLs.return_(created_rental.id))

        assert response.status_code == StatusCode.OK
        rental = RentalRead.model_validate(response.json())
        assert rental.is_returned is True
        assert rental.returned_at is not None
        copies_after = client.get(MovieURLs.detail(created_movie.id)).json()["available_copies"]
        assert copies_after == copies_before + 1

    def test_already_returned(self, client: httpx.Client, created_rental: RentalRead):
        client.post(RentalURLs.return_(created_rental.id))
        response = client.post(RentalURLs.return_(created_rental.id))

        assert response.status_code == StatusCode.CONFLICT
        assert response.json()["detail"] == "Already returned"

    def test_return_not_found(self, client: httpx.Client):
        response = client.post(RentalURLs.return_(9999))

        assert response.status_code == StatusCode.NOT_FOUND
