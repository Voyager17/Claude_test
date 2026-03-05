from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.movie import Movie
from app.models.rental import Rental


class DBQueries:
    def __init__(self, db: Session) -> None:
        self.db = db

    # --- Movies ---

    def select_movie(self, movie_id: int):
        query = text("SELECT * FROM movies WHERE id = :id")
        return self.db.query(Movie).from_statement(query).params(id=movie_id).first()

    def select_movies(self):
        query = text("SELECT * FROM movies")
        return self.db.execute(query).all()

    def select_active_movies(self):
        query = text("SELECT * FROM movies WHERE is_active = 1")
        return self.db.execute(query).all()

    def count_movies(self) -> int:
        query = text("SELECT COUNT(*) FROM movies")
        return self.db.execute(query).scalar()

    def count_active_movies(self) -> int:
        query = text("SELECT COUNT(*) FROM movies WHERE is_active = 1")
        return self.db.execute(query).scalar()

    # --- Customers ---

    def select_customer(self, customer_id: int):
        query = text("SELECT * FROM customers WHERE id = :id")
        return self.db.query(Customer).from_statement(query).params(id=customer_id).first()

    def select_customer_by_email(self, email: str):
        query = text("SELECT * FROM customers WHERE email = :email")
        return self.db.execute(query, {"email": email}).first()

    def select_customers(self):
        query = text("SELECT * FROM customers")
        return self.db.execute(query).all()

    def select_active_customers(self):
        query = text("SELECT * FROM customers WHERE is_active = 1")
        return self.db.execute(query).all()

    def count_customers(self) -> int:
        query = text("SELECT COUNT(*) FROM customers")
        return self.db.execute(query).scalar()

    # --- Rentals ---

    def select_rental(self, rental_id: int):
        query = text("SELECT * FROM rentals WHERE id = :id")
        return self.db.query(Rental).from_statement(query).params(id=rental_id).first()

    def select_rentals(self):
        query = text("SELECT * FROM rentals")
        return self.db.execute(query).all()

    def select_active_rentals(self):
        query = text("SELECT * FROM rentals WHERE is_returned = 0")
        return self.db.execute(query).all()

    def select_rentals_by_customer(self, customer_id: int):
        query = text("SELECT * FROM rentals WHERE customer_id = :customer_id")
        return self.db.execute(query, {"customer_id": customer_id}).all()

    def select_rentals_by_movie(self, movie_id: int):
        query = text("SELECT * FROM rentals WHERE movie_id = :movie_id")
        return self.db.execute(query, {"movie_id": movie_id}).all()

    def count_rentals(self) -> int:
        query = text("SELECT COUNT(*) FROM rentals")
        return self.db.execute(query).scalar()

    def count_active_rentals(self) -> int:
        query = text("SELECT COUNT(*) FROM rentals WHERE is_returned = 0")
        return self.db.execute(query).scalar()
