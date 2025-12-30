import datetime as dt

from pydantic import BaseModel, ConfigDict, Field


class TripBase(BaseModel):
    departure_date: dt.date
    return_date: dt.date

    origin: str = Field(..., max_length=120)
    destination: str = Field(..., max_length=120)
    distance_km: int = Field(..., ge=0)

    car_number: str = Field(..., max_length=32)
    driver_tab_number: str = Field(..., max_length=32)


class TripCreate(TripBase):
    pass


class TripUpdate(BaseModel):
    departure_date: dt.date | None = None
    return_date: dt.date | None = None
    origin: str | None = Field(None, max_length=120)
    destination: str | None = Field(None, max_length=120)
    distance_km: int | None = Field(None, ge=0)
    car_number: str | None = Field(None, max_length=32)
    driver_tab_number: str | None = Field(None, max_length=32)


class TripRead(TripBase):
    model_config = ConfigDict(from_attributes=True)

    id: int