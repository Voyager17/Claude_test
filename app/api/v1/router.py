from fastapi import APIRouter

from app.api.v1.endpoints import auth, customers, movies, rentals

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(movies.router)
api_router.include_router(customers.router)
api_router.include_router(rentals.router)
