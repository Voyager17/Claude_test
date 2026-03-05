from datetime import datetime
from pydantic import BaseModel, Field


class RentalCreate(BaseModel):
    customer_id: int
    movie_id: int
    rental_days: int = Field(ge=1, default=1)


class RentalRead(BaseModel):
    id: int
    customer_id: int
    movie_id: int
    rented_at: datetime
    due_date: datetime
    returned_at: datetime | None
    total_price: float
    is_returned: bool

    model_config = {"from_attributes": True}
