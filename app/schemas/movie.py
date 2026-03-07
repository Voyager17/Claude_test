import random
import uuid

from pydantic import BaseModel, Field

_GENRES = ["Drama", "Action", "Sci-Fi", "Comedy", "Thriller", "Crime", "History"]


class MovieBase(BaseModel):
    title: str
    director: str
    year: int = Field(ge=1888)
    genre: str
    rating: float = Field(ge=0.0, le=10.0, default=0.0)
    rental_price_per_day: float = Field(gt=0)
    available_copies: int = Field(ge=0, default=1)
    image_url: str | None = None
    description: str | None = None


class MovieCreate(MovieBase):
    @classmethod
    def rand_init(cls) -> "MovieCreate":
        return cls(
            title=f"Movie {uuid.uuid4().hex[:8]}",
            director=f"Director {uuid.uuid4().hex[:6]}",
            year=random.randint(1950, 2024),
            genre=random.choice(_GENRES),
            rating=round(random.uniform(1.0, 10.0), 1),
            rental_price_per_day=round(random.uniform(0.5, 5.0), 2),
            available_copies=random.randint(1, 5),
        )


class MovieUpdate(BaseModel):
    title: str | None = None
    director: str | None = None
    year: int | None = Field(default=None, ge=1888)
    genre: str | None = None
    rating: float | None = Field(default=None, ge=0.0, le=10.0)
    rental_price_per_day: float | None = Field(default=None, gt=0)
    available_copies: int | None = Field(default=None, ge=0)
    image_url: str | None = None
    description: str | None = None


class MovieRead(MovieBase):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}
