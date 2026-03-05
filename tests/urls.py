from app.main import app


class MovieURLs:
    base = str(app.url_path_for("list_movies"))

    @staticmethod
    def detail(movie_id: int) -> str:
        return str(app.url_path_for("get_movie", movie_id=movie_id))


class CustomerURLs:
    base = str(app.url_path_for("list_customers"))

    @staticmethod
    def detail(customer_id: int) -> str:
        return str(app.url_path_for("get_customer", customer_id=customer_id))


class RentalURLs:
    base = str(app.url_path_for("list_rentals"))

    @staticmethod
    def detail(rental_id: int) -> str:
        return str(app.url_path_for("get_rental", rental_id=rental_id))

    @staticmethod
    def return_(rental_id: int) -> str:
        return str(app.url_path_for("return_rental", rental_id=rental_id))
