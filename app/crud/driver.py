from sqlalchemy import Select, asc, desc, select
from sqlalchemy.orm import Session

from app.models.driver import Driver
from app.schemas.driver import DriverCreate, DriverUpdate


def create_driver(db: Session, obj_in: DriverCreate) -> Driver:
    db_obj = Driver(**obj_in.model_dump())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_driver(db: Session, tab_number: str) -> Driver | None:
    return db.get(Driver, tab_number)


def list_drivers(
    db: Session,
    *,
    offset: int = 0,
    limit: int = 50,
    sort_by: str = "tab_number",
    sort_dir: str = "asc",
) -> list[Driver]:
    sort_map = {
        "tab_number": Driver.tab_number,
        "full_name": Driver.full_name,
        "category": Driver.category,
    }
    sort_col = sort_map.get(sort_by, Driver.tab_number)
    order = asc(sort_col) if sort_dir.lower() == "asc" else desc(sort_col)

    stmt: Select[tuple[Driver]] = select(Driver).order_by(order).offset(offset).limit(limit)
    return list(db.scalars(stmt).all())


def update_driver(db: Session, db_obj: Driver, obj_in: DriverUpdate) -> Driver:
    data = obj_in.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(db_obj, k, v)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_driver(db: Session, db_obj: Driver) -> None:
    db.delete(db_obj)
    db.commit()