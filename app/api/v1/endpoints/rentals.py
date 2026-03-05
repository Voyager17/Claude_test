from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.customer import Customer
from app.models.movie import Movie
from app.models.rental import Rental
from app.schemas.rental import RentalCreate, RentalRead

router = APIRouter(prefix="/rentals", tags=["rentals"])


@router.get("/", response_model=list[RentalRead])
def list_rentals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Rental).offset(skip).limit(limit).all()


@router.get("/{rental_id}", response_model=RentalRead)
def get_rental(rental_id: int, db: Session = Depends(get_db)):
    rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rental not found")
    return rental


@router.post("/", response_model=RentalRead, status_code=status.HTTP_201_CREATED)
def create_rental(payload: RentalCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == payload.customer_id, Customer.is_active == True).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")

    movie = db.query(Movie).filter(Movie.id == payload.movie_id, Movie.is_active == True).first()
    if not movie:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")

    if movie.available_copies < 1:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="No copies available")

    now = datetime.utcnow()
    rental = Rental(
        customer_id=payload.customer_id,
        movie_id=payload.movie_id,
        rented_at=now,
        due_date=now + timedelta(days=payload.rental_days),
        total_price=movie.rental_price_per_day * payload.rental_days,
    )
    movie.available_copies -= 1
    db.add(rental)
    db.commit()
    db.refresh(rental)
    return rental


@router.post("/{rental_id}/return", response_model=RentalRead)
def return_rental(rental_id: int, db: Session = Depends(get_db)):
    rental = db.query(Rental).filter(Rental.id == rental_id).first()
    if not rental:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rental not found")
    if rental.is_returned:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already returned")

    rental.is_returned = True
    rental.returned_at = datetime.utcnow()

    movie = db.query(Movie).filter(Movie.id == rental.movie_id).first()
    if movie:
        movie.available_copies += 1

    db.commit()
    db.refresh(rental)
    return rental
