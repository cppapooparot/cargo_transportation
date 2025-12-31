import datetime as dt

from sqlalchemy import Select, asc, desc, func, select, update
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


def search_trips(
    db: Session,
    *,
    origin: str | None = None,
    destination: str | None = None,
    min_distance_km: int | None = None,
    max_distance_km: int | None = None,
    from_date: dt.date | None = None,
    to_date: dt.date | None = None,
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

    stmt: Select[tuple[Trip]] = select(Trip)
    if origin is not None:
        stmt = stmt.where(Trip.origin == origin)
    if destination is not None:
        stmt = stmt.where(Trip.destination == destination)
    if min_distance_km is not None:
        stmt = stmt.where(Trip.distance_km >= min_distance_km)
    if max_distance_km is not None:
        stmt = stmt.where(Trip.distance_km <= max_distance_km)
    if from_date is not None:
        stmt = stmt.where(Trip.departure_date >= from_date)
    if to_date is not None:
        stmt = stmt.where(Trip.departure_date <= to_date)

    stmt = stmt.order_by(order).offset(offset).limit(limit)
    return list(db.scalars(stmt).all())


def list_trips_with_details(
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

    stmt: Select[tuple[Trip]] = (
        select(Trip)
        .join(Trip.car)
        .join(Trip.driver)
        .order_by(order)
        .offset(offset)
        .limit(limit)
    )
    return list(db.scalars(stmt).unique().all())


def bulk_increase_distance(
    db: Session,
    *,
    origin: str,
    min_distance_km: int,
    add_km: int,
) -> int:
    stmt = (
        update(Trip)
        .where(Trip.origin == origin)
        .where(Trip.distance_km >= min_distance_km)
        .values(distance_km=Trip.distance_km + add_km)
    )
    res = db.execute(stmt)
    db.commit()
    return int(res.rowcount or 0)


def report_fuel_by_brand(
    db: Session,
    *,
    from_date: dt.date | None = None,
    to_date: dt.date | None = None,
    offset: int = 0,
    limit: int = 50,
    sort_dir: str = "desc",
) -> list[tuple[str, int, int, float]]:
    from app.models.car import Car

    stmt = (
        select(
            Car.brand,
            func.count(Trip.id).label("trips_count"),
            func.coalesce(func.sum(Trip.distance_km), 0).label("total_distance_km"),
            func.coalesce(
                func.sum((Trip.distance_km * Car.fuel_l_per_100km) / 100.0),
                0.0,
            ).label("est_total_fuel_l"),
        )
        .join(Car, Trip.car_number == Car.number)
        .group_by(Car.brand)
    )

    if from_date is not None:
        stmt = stmt.where(Trip.departure_date >= from_date)
    if to_date is not None:
        stmt = stmt.where(Trip.departure_date <= to_date)

    order = desc("total_distance_km") if sort_dir.lower() == "desc" else asc("total_distance_km")
    stmt = stmt.order_by(order).offset(offset).limit(limit)
    return list(db.execute(stmt).all())