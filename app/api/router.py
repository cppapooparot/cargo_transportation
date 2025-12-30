from fastapi import APIRouter

from app.api.routes.cars import router as cars_router
from app.api.routes.drivers import router as drivers_router
from app.api.routes.trips import router as trips_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(cars_router)
api_router.include_router(drivers_router)
api_router.include_router(trips_router)