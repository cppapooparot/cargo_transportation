import datetime as dt

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Trip(Base):
    __tablename__ = "trips"

    id: Mapped[int] = mapped_column(primary_key=True)

    departure_date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    return_date: Mapped[dt.date] = mapped_column(Date, nullable=False)

    origin: Mapped[str] = mapped_column(String(120), nullable=False)
    destination: Mapped[str] = mapped_column(String(120), nullable=False)
    distance_km: Mapped[int] = mapped_column(Integer, nullable=False)

    car_number: Mapped[str] = mapped_column(ForeignKey("cars.number"), nullable=False)
    driver_tab_number: Mapped[str] = mapped_column(
        ForeignKey("drivers.tab_number"), nullable=False
    )
    
    car = relationship("Car", back_populates="trips")
    driver = relationship("Driver", back_populates="trips")