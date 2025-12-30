from pydantic import BaseModel, ConfigDict, Field


class CarBase(BaseModel):
    brand: str = Field(..., max_length=120)
    capacity_kg: int = Field(..., ge=0)
    fuel_l_per_100km: int = Field(..., ge=0)


class CarCreate(CarBase):
    number: str = Field(..., max_length=32)


class CarUpdate(BaseModel):
    brand: str | None = Field(None, max_length=120)
    capacity_kg: int | None = Field(None, ge=0)
    fuel_l_per_100km: int | None = Field(None, ge=0)


class CarRead(CarBase):
    model_config = ConfigDict(from_attributes=True)

    number: str