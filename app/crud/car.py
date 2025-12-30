from sqlalchemy import Select, asc, desc, select
from sqlalchemy.orm import Session

from app.models.car import Car
from app.schemas.car import CarCreate, CarUpdate


def create_car(db: Session, obj_in: CarCreate) -> Car:
    db_obj = Car(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_car(db: Session, number: str) -> Car | None:
    return db.get(Car, number)


def list_cars(
    db: Session,
    *,
    offset: int = 0,
    limit: int = 50,
    sort_by: str = "number",
    sort_dir: str = "asc",
) -> list[Car]:
    sort_map = {
        "number": Car.number,
        "brand": Car.brand,
        "capacity_kg": Car.capacity_kg,
        "fuel_l_per_100km": Car.fuel_l_per_100km,
    }
    sort_col = sort_map.get(sort_by, Car.number)
    order = asc(sort_col) if sort_dir.lower() == "asc" else desc(sort_col)

    stmt: Select[tuple[Car]] = select(Car).order_by(order).offset(offset).limit(limit)
    return list(db.scalars(stmt).all())


def update_car(db: Session, db_obj: Car, obj_in: CarUpdate) -> Car:
    data = obj_in.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(db_obj, k, v)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_car(db: Session, db_obj: Car) -> None:
    db.delete(db_obj)
    db.commit()