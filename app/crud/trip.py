from sqlalchemy import Select, asc, desc, select
from sqlalchemy.orm import Session

from app.models.trip import Trip
from app.schemas.trip import TripCreate, TripUpdate


def create_trip(db: Session, obj_in: TripCreate) -> Trip:
    db_obj = Trip(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_trip(db: Session, trip_id: int) -> Trip | None:
    return db.get(Trip, trip_id)


def list_trips(
    db: Session,
    *,
    offset: int = 0,
    limit: int = 50,
    sort_by: str = "id",
    sort_dir: str = "asc",
) -> list[Trip]:
    sort_map = {
        "id": Trip.id,
        "departure_date": Trip.departure_date,
        "return_date": Trip.return_date,
        "distance_km": Trip.distance_km,
        "origin": Trip.origin,
        "destination": Trip.destination,
    }
    sort_col = sort_map.get(sort_by, Trip.id)
    order = asc(sort_col) if sort_dir.lower() == "asc" else desc(sort_col)

    stmt: Select[tuple[Trip]] = select(Trip).order_by(order).offset(offset).limit(limit)
    return list(db.scalars(stmt).all())


def update_trip(db: Session, db_obj: Trip, obj_in: TripUpdate) -> Trip:
    data = obj_in.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(db_obj, k, v)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_trip(db: Session, db_obj: Trip) -> None:
    db.delete(db_obj)
    db.commit()