from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    building: Mapped[str] = mapped_column(String(120))
    floor: Mapped[str] = mapped_column(String(40))
    room_number: Mapped[str] = mapped_column(String(40))
    room_type: Mapped[str] = mapped_column(String(80))
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity: Mapped[float | None] = mapped_column(Float, nullable=True)
    occupancy: Mapped[int] = mapped_column(Integer, default=0)
    active_mode: Mapped[str] = mapped_column(String(80), default="Monitoring")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    devices: Mapped[list["Device"]] = relationship(back_populates="room", cascade="all, delete-orphan")
