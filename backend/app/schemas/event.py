from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class EventCreate(BaseModel):
    event_type: str = Field(min_length=1, max_length=80)
    location: str = Field(min_length=1, max_length=120)
    description: str = Field(min_length=1)
    timestamp: datetime | None = None
    metadata_: dict[str, Any] | None = Field(default=None, alias="metadata", validation_alias=AliasChoices("metadata_", "metadata"), serialization_alias="metadata")

    model_config = ConfigDict(populate_by_name=True)


class EventRead(EventCreate):
    id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
