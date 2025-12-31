import datetime as dt

from pydantic import BaseModel, ConfigDict, Field


class TripDetailsCar(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    number: str
    brand: str
    capacity_kg: int
    fuel_l_per_100km: int


class TripDetailsDriver(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tab_number: str
    full_name: str
    category: str


class TripWithDetailsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    departure_date: dt.date
    return_date: dt.date
    origin: str
    destination: str
    distance_km: int
    cargo: dict = Field(default_factory=dict)

    car: TripDetailsCar
    driver: TripDetailsDriver


class FuelByBrandRow(BaseModel):
    brand: str
    trips_count: int
    total_distance_km: int
    est_total_fuel_l: float
