from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Car(Base):
    __tablename__ = "cars"

    number: Mapped[str] = mapped_column(String(32), primary_key=True)
    brand: Mapped[str] = mapped_column(String(120), nullable=False)
    capacity_kg: Mapped[int] = mapped_column(Integer, nullable=False)
    fuel_l_per_100km: Mapped[int] = mapped_column(Integer, nullable=False)

    trips = relationship("Trip", back_populates="car")