from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    device_type: Mapped[str] = mapped_column(String(80))
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    status: Mapped[str] = mapped_column(String(60), default="standby")
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    metadata_: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    room: Mapped["Room"] = relationship(back_populates="devices")
