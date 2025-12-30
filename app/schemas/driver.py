from pydantic import BaseModel, ConfigDict, Field


class DriverBase(BaseModel):
    full_name: str = Field(..., max_length=200)
    category: str = Field(..., max_length=8)


class DriverCreate(DriverBase):
    tab_number: str = Field(..., max_length=32)


class DriverUpdate(BaseModel):
    full_name: str | None = Field(None, max_length=200)
    category: str | None = Field(None, max_length=8)


class DriverRead(DriverBase):
    model_config = ConfigDict(from_attributes=True)

    tab_number: str