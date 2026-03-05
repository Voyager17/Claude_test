from pydantic import BaseModel, Field


class MovieBase(BaseModel):
    title: str
    director: str
    year: int = Field(ge=1888)
    genre: str
    rating: float = Field(ge=0.0, le=10.0, default=0.0)
    rental_price_per_day: float = Field(gt=0)
    available_copies: int = Field(ge=0, default=1)


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    title: str | None = None
    director: str | None = None
    year: int | None = Field(default=None, ge=1888)
    genre: str | None = None
    rating: float | None = Field(default=None, ge=0.0, le=10.0)
    rental_price_per_day: float | None = Field(default=None, gt=0)
    available_copies: int | None = Field(default=None, ge=0)


class MovieRead(MovieBase):
    id: int
    is_active: bool

    model_config = {"from_attributes": True}
