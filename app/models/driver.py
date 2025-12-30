from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Driver(Base):
    __tablename__ = "drivers"

    tab_number: Mapped[str] = mapped_column(String(32), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(8), nullable=False)

    trips = relationship("Trip", back_populates="driver")