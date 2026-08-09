from pydantic import BaseModel


class SystemStatus(BaseModel):
    backend: str
    database: str
    llm: str
    rooms: int
    devices: int
    recent_events: int
