from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class DeviceBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    device_type: str
    room_id: int
    status: str = "standby"
    is_online: bool = False
    metadata_: dict[str, Any] | None = Field(default=None, alias="metadata", validation_alias=AliasChoices("metadata_", "metadata"), serialization_alias="metadata")

    model_config = ConfigDict(populate_by_name=True)


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: str | None = None
    device_type: str | None = None
    room_id: int | None = None
    status: str | None = None
    is_online: bool | None = None
    metadata_: dict[str, Any] | None = Field(default=None, alias="metadata", validation_alias=AliasChoices("metadata_", "metadata"), serialization_alias="metadata")

    model_config = ConfigDict(populate_by_name=True)


class DeviceRead(DeviceBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
