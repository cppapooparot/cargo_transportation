from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.car import create_car, delete_car, get_car, list_cars, update_car
from app.schemas.car import CarCreate, CarRead, CarUpdate

router = APIRouter(prefix="/cars", tags=["cars"])


@router.post("", response_model=CarRead, status_code=status.HTTP_201_CREATED)
def create_car_endpoint(payload: CarCreate, db: Session = Depends(get_db)) -> CarRead:
    existing = get_car(db, payload.number)
    if existing is not None:
        raise HTTPException(status_code=409, detail="Car with this number already exists")
    return create_car(db, payload)


@router.get("", response_model=list[CarRead])
def list_cars_endpoint(
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    sort_by: str = Query("number", pattern="^(number|brand|capacity_kg|fuel_l_per_100km)$"),
    sort_dir: str = Query("asc", pattern="^(asc|desc)$"),
) -> list[CarRead]:
    return list_cars(db, offset=offset, limit=limit, sort_by=sort_by, sort_dir=sort_dir)


@router.get("/{number}", response_model=CarRead)
def get_car_endpoint(number: str, db: Session = Depends(get_db)) -> CarRead:
    db_obj = get_car(db, number)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return db_obj


@router.patch("/{number}", response_model=CarRead)
def update_car_endpoint(number: str, payload: CarUpdate, db: Session = Depends(get_db)) -> CarRead:
    db_obj = get_car(db, number)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Car not found")
    return update_car(db, db_obj, payload)


@router.delete("/{number}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car_endpoint(number: str, db: Session = Depends(get_db)) -> None:
    db_obj = get_car(db, number)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Car not found")
    delete_car(db, db_obj)
    return None