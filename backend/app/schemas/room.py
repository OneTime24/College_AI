from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.device import DeviceRead


class RoomBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    building: str
    floor: str
    room_number: str
    room_type: str
    temperature: float | None = None
    humidity: float | None = None
    occupancy: int = Field(default=0, ge=0)
    active_mode: str = "Monitoring"


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    building: str | None = None
    floor: str | None = None
    room_number: str | None = None
    room_type: str | None = None
    temperature: float | None = None
    humidity: float | None = None
    occupancy: int | None = Field(default=None, ge=0)
    active_mode: str | None = None


class RoomRead(RoomBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RoomDetail(RoomRead):
    devices: list[DeviceRead] = []
