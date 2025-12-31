import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.car import get_car
from app.crud.driver import get_driver
from app.crud.trip import (
    bulk_increase_distance,
    create_trip,
    delete_trip,
    get_trip,
    list_trips,
    list_trips_with_details,
    search_trips,
    update_trip,
)
from app.models.trip import Trip
from app.schemas.reports import TripWithDetailsRead
from app.schemas.trip import TripCreate, TripRead, TripUpdate

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post("", response_model=TripRead, status_code=status.HTTP_201_CREATED)
def create_trip_endpoint(payload: TripCreate, db: Session = Depends(get_db)) -> TripRead:
    if get_car(db, payload.car_number) is None:
        raise HTTPException(status_code=400, detail="car_number does not exist")
    if get_driver(db, payload.driver_tab_number) is None:
        raise HTTPException(status_code=400, detail="driver_tab_number does not exist")
    if payload.return_date < payload.departure_date:
        raise HTTPException(status_code=400, detail="return_date must be >= departure_date")
    return create_trip(db, payload)


@router.get("", response_model=list[TripRead])
def list_trips_endpoint(
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    sort_by: str = Query("id", pattern="^(id|departure_date|return_date|distance_km|origin|destination)$"),
    sort_dir: str = Query("asc", pattern="^(asc|desc)$"),
) -> list[TripRead]:
    return list_trips(db, offset=offset, limit=limit, sort_by=sort_by, sort_dir=sort_dir)


@router.get("/{trip_id}", response_model=TripRead)
def get_trip_endpoint(trip_id: int, db: Session = Depends(get_db)) -> TripRead:
    db_obj = get_trip(db, trip_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return db_obj


@router.patch("/{trip_id}", response_model=TripRead)
def update_trip_endpoint(trip_id: int, payload: TripUpdate, db: Session = Depends(get_db)) -> TripRead:
    db_obj = get_trip(db, trip_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Trip not found")

    if payload.car_number is not None and get_car(db, payload.car_number) is None:
        raise HTTPException(status_code=400, detail="car_number does not exist")
    if payload.driver_tab_number is not None and get_driver(db, payload.driver_tab_number) is None:
        raise HTTPException(status_code=400, detail="driver_tab_number does not exist")

    dep = payload.departure_date or db_obj.departure_date
    ret = payload.return_date or db_obj.return_date
    if ret < dep:
        raise HTTPException(status_code=400, detail="return_date must be >= departure_date")

    return update_trip(db, db_obj, payload)


@router.delete("/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_trip_endpoint(trip_id: int, db: Session = Depends(get_db)) -> None:
    db_obj = get_trip(db, trip_id)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    delete_trip(db, db_obj)
    return None


@router.get("/search-cargo", response_model=list[TripRead])
def search_trips_by_cargo_regex(
    pattern: str = Query(..., min_length=1, max_length=200),
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[TripRead]:
    stmt = (
        select(Trip)
        .where(text("cargo::text ~* :pattern"))
        .params(pattern=pattern)
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(stmt).all())


@router.get("/search", response_model=list[TripRead])
def search_trips_endpoint(
    db: Session = Depends(get_db),
    origin: str | None = Query(None, max_length=120),
    destination: str | None = Query(None, max_length=120),
    min_distance_km: int | None = Query(None, ge=0),
    max_distance_km: int | None = Query(None, ge=0),
    from_date: dt.date | None = Query(None),
    to_date: dt.date | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    sort_by: str = Query("id", pattern="^(id|departure_date|return_date|distance_km|origin|destination)$"),
    sort_dir: str = Query("asc", pattern="^(asc|desc)$"),
) -> list[TripRead]:
    return search_trips(
        db,
        origin=origin,
        destination=destination,
        min_distance_km=min_distance_km,
        max_distance_km=max_distance_km,
        from_date=from_date,
        to_date=to_date,
        offset=offset,
        limit=limit,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )


@router.get("/with-details", response_model=list[TripWithDetailsRead])
def trips_with_details_endpoint(
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    sort_by: str = Query("id", pattern="^(id|departure_date|return_date|distance_km|origin|destination)$"),
    sort_dir: str = Query("asc", pattern="^(asc|desc)$"),
) -> list[TripWithDetailsRead]:
    return list_trips_with_details(db, offset=offset, limit=limit, sort_by=sort_by, sort_dir=sort_dir)


@router.post("/bulk-increase-distance")
def bulk_increase_distance_endpoint(
    db: Session = Depends(get_db),
    origin: str = Query(..., max_length=120),
    min_distance_km: int = Query(0, ge=0),
    add_km: int = Query(..., ge=1, le=100000),
) -> dict:
    updated = bulk_increase_distance(db, origin=origin, min_distance_km=min_distance_km, add_km=add_km)
    return {"updated": updated}