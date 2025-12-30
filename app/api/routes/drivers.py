from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.driver import create_driver, delete_driver, get_driver, list_drivers, update_driver
from app.schemas.driver import DriverCreate, DriverRead, DriverUpdate

router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.post("", response_model=DriverRead, status_code=status.HTTP_201_CREATED)
def create_driver_endpoint(payload: DriverCreate, db: Session = Depends(get_db)) -> DriverRead:
    existing = get_driver(db, payload.tab_number)
    if existing is not None:
        raise HTTPException(status_code=409, detail="Driver with this tab_number already exists")
    return create_driver(db, payload)


@router.get("", response_model=list[DriverRead])
def list_drivers_endpoint(
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    sort_by: str = Query("tab_number", pattern="^(tab_number|full_name|category)$"),
    sort_dir: str = Query("asc", pattern="^(asc|desc)$"),
) -> list[DriverRead]:
    return list_drivers(db, offset=offset, limit=limit, sort_by=sort_by, sort_dir=sort_dir)


@router.get("/{tab_number}", response_model=DriverRead)
def get_driver_endpoint(tab_number: str, db: Session = Depends(get_db)) -> DriverRead:
    db_obj = get_driver(db, tab_number)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    return db_obj


@router.patch("/{tab_number}", response_model=DriverRead)
def update_driver_endpoint(tab_number: str, payload: DriverUpdate, db: Session = Depends(get_db)) -> DriverRead:
    db_obj = get_driver(db, tab_number)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    return update_driver(db, db_obj, payload)


@router.delete("/{tab_number}", status_code=status.HTTP_204_NO_CONTENT)
def delete_driver_endpoint(tab_number: str, db: Session = Depends(get_db)) -> None:
    db_obj = get_driver(db, tab_number)
    if db_obj is None:
        raise HTTPException(status_code=404, detail="Driver not found")
    delete_driver(db, db_obj)
    return None