import datetime as dt

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud.trip import report_fuel_by_brand
from app.schemas.reports import FuelByBrandRow

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/fuel-by-brand", response_model=list[FuelByBrandRow])
def fuel_by_brand(
    db: Session = Depends(get_db),
    from_date: dt.date | None = Query(None),
    to_date: dt.date | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    sort_dir: str = Query("desc", pattern="^(asc|desc)$"),
) -> list[FuelByBrandRow]:
    rows = report_fuel_by_brand(
        db,
        from_date=from_date,
        to_date=to_date,
        offset=offset,
        limit=limit,
        sort_dir=sort_dir,
    )
    return [
        FuelByBrandRow(
            brand=brand,
            trips_count=trips_count,
            total_distance_km=total_distance_km,
            est_total_fuel_l=float(est_total_fuel_l),
        )
        for (brand, trips_count, total_distance_km, est_total_fuel_l) in rows
    ]
