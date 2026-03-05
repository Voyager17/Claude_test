from sqlalchemy import Column, Integer, String, Float, Boolean
from app.core.database import Base


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    director = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    genre = Column(String, nullable=False)
    rating = Column(Float, default=0.0)
    rental_price_per_day = Column(Float, nullable=False)
    available_copies = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
