from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal, engine
from app.models import Movie, Customer, Rental
from app.core.database import Base

Base.metadata.create_all(bind=engine)

db = SessionLocal()

movies = [
    Movie(title="The Shawshank Redemption", director="Frank Darabont", year=1994, genre="Drama", rating=9.3, rental_price_per_day=1.99, available_copies=3),
    Movie(title="The Godfather", director="Francis Ford Coppola", year=1972, genre="Crime", rating=9.2, rental_price_per_day=2.49, available_copies=2),
    Movie(title="Pulp Fiction", director="Quentin Tarantino", year=1994, genre="Crime", rating=8.9, rental_price_per_day=1.99, available_copies=4),
    Movie(title="Schindler's List", director="Steven Spielberg", year=1993, genre="History", rating=9.0, rental_price_per_day=1.49, available_copies=2),
    Movie(title="The Dark Knight", director="Christopher Nolan", year=2008, genre="Action", rating=9.0, rental_price_per_day=2.99, available_copies=5),
    Movie(title="Forrest Gump", director="Robert Zemeckis", year=1994, genre="Drama", rating=8.8, rental_price_per_day=1.49, available_copies=3),
    Movie(title="Inception", director="Christopher Nolan", year=2010, genre="Sci-Fi", rating=8.8, rental_price_per_day=2.99, available_copies=4),
    Movie(title="The Matrix", director="Wachowski Sisters", year=1999, genre="Sci-Fi", rating=8.7, rental_price_per_day=1.99, available_copies=3),
    Movie(title="Goodfellas", director="Martin Scorsese", year=1990, genre="Crime", rating=8.7, rental_price_per_day=1.99, available_copies=2),
    Movie(title="Se7en", director="David Fincher", year=1995, genre="Thriller", rating=8.6, rental_price_per_day=1.49, available_copies=3),
]

customers = [
    Customer(full_name="Иван Петров", email="ivan.petrov@mail.ru", phone="+7-916-123-45-67"),
    Customer(full_name="Мария Сидорова", email="m.sidorova@gmail.com", phone="+7-903-987-65-43"),
    Customer(full_name="Алексей Козлов", email="a.kozlov@yandex.ru", phone="+7-926-555-12-34"),
    Customer(full_name="Ольга Новикова", email="o.novikova@mail.ru", phone="+7-965-777-88-99"),
    Customer(full_name="Дмитрий Морозов", email="d.morozov@gmail.com", phone=None),
]

db.add_all(movies)
db.add_all(customers)
db.commit()

now = datetime.utcnow()

rentals = [
    # завершённые аренды
    Rental(customer_id=1, movie_id=1, rented_at=now - timedelta(days=10), due_date=now - timedelta(days=7), returned_at=now - timedelta(days=8), total_price=3 * 1.99, is_returned=True),
    Rental(customer_id=2, movie_id=3, rented_at=now - timedelta(days=5), due_date=now - timedelta(days=2), returned_at=now - timedelta(days=3), total_price=3 * 1.99, is_returned=True),
    Rental(customer_id=3, movie_id=5, rented_at=now - timedelta(days=8), due_date=now - timedelta(days=5), returned_at=now - timedelta(days=6), total_price=3 * 2.99, is_returned=True),
    # активные аренды
    Rental(customer_id=1, movie_id=7, rented_at=now - timedelta(days=2), due_date=now + timedelta(days=5), total_price=7 * 2.99, is_returned=False),
    Rental(customer_id=4, movie_id=2, rented_at=now - timedelta(days=1), due_date=now + timedelta(days=2), total_price=3 * 2.49, is_returned=False),
    Rental(customer_id=5, movie_id=8, rented_at=now, due_date=now + timedelta(days=3), total_price=3 * 1.99, is_returned=False),
]

# уменьшаем available_copies для активных аренд
movies[6].available_copies -= 1  # Inception
movies[1].available_copies -= 1  # The Godfather
movies[7].available_copies -= 1  # The Matrix

db.add_all(rentals)
db.commit()
db.close()

print(f"Добавлено: {len(movies)} фильмов, {len(customers)} клиентов, {len(rentals)} аренд")
