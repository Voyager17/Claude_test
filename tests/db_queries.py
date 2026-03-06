from contextlib import contextmanager

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker

from app.models.customer import Customer
from app.models.movie import Movie
from app.models.rental import Rental


class DBQueries:
    def __init__(self, session_maker: sessionmaker) -> None:
        self._maker = session_maker

    @contextmanager
    def _db(self):
        session = self._maker()
        try:
            yield session
        finally:
            session.close()

    # --- Movies ---

    def select_movie(self, movie_id: int):
        with self._db() as db:
            obj = db.query(Movie).from_statement(
                text("SELECT * FROM movies WHERE id = :id")
            ).params(id=movie_id).first()
            if obj:
                db.expunge(obj)
            return obj

    def select_movies(self):
        with self._db() as db:
            return db.execute(text("SELECT * FROM movies")).all()

    def select_active_movies(self):
        with self._db() as db:
            return db.execute(text("SELECT * FROM movies WHERE is_active = true")).all()

    def count_movies(self) -> int:
        with self._db() as db:
            return db.execute(text("SELECT COUNT(*) FROM movies")).scalar()

    def count_active_movies(self) -> int:
        with self._db() as db:
            return db.execute(text("SELECT COUNT(*) FROM movies WHERE is_active = true")).scalar()

    # --- Customers ---

    def select_customer(self, customer_id: int):
        with self._db() as db:
            obj = db.query(Customer).from_statement(
                text("SELECT * FROM customers WHERE id = :id")
            ).params(id=customer_id).first()
            if obj:
                db.expunge(obj)
            return obj

    def select_customer_by_email(self, email: str):
        with self._db() as db:
            return db.execute(text("SELECT * FROM customers WHERE email = :email"), {"email": email}).first()

    def select_customers(self):
        with self._db() as db:
            return db.execute(text("SELECT * FROM customers")).all()

    def select_active_customers(self):
        with self._db() as db:
            return db.execute(text("SELECT * FROM customers WHERE is_active = true")).all()

    def count_customers(self) -> int:
        with self._db() as db:
            return db.execute(text("SELECT COUNT(*) FROM customers")).scalar()

    # --- Rentals ---

    def select_rental(self, rental_id: int):
        with self._db() as db:
            obj = db.query(Rental).from_statement(
                text("SELECT * FROM rentals WHERE id = :id")
            ).params(id=rental_id).first()
            if obj:
                db.expunge(obj)
            return obj

    def select_rentals(self):
        with self._db() as db:
            return db.execute(text("SELECT * FROM rentals")).all()

    def select_active_rentals(self):
        with self._db() as db:
            return db.execute(text("SELECT * FROM rentals WHERE is_returned = false")).all()

    def select_rentals_by_customer(self, customer_id: int):
        with self._db() as db:
            return db.execute(text("SELECT * FROM rentals WHERE customer_id = :customer_id"), {"customer_id": customer_id}).all()

    def select_rentals_by_movie(self, movie_id: int):
        with self._db() as db:
            return db.execute(text("SELECT * FROM rentals WHERE movie_id = :movie_id"), {"movie_id": movie_id}).all()

    def count_rentals(self) -> int:
        with self._db() as db:
            return db.execute(text("SELECT COUNT(*) FROM rentals")).scalar()

    def count_active_rentals(self) -> int:
        with self._db() as db:
            return db.execute(text("SELECT COUNT(*) FROM rentals WHERE is_returned = false")).scalar()
