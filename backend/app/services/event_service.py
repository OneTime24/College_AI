from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.event import Event
from app.schemas.event import EventCreate


def list_events(db: Session, limit: int = 50, location: str | None = None, event_type: str | None = None) -> list[Event]:
    statement = select(Event)
    if location:
        statement = statement.where(Event.location == location)
    if event_type:
        statement = statement.where(Event.event_type == event_type)
    return list(db.scalars(statement.order_by(Event.timestamp.desc()).limit(limit)))


def create_event(db: Session, payload: EventCreate) -> Event:
    event = Event(**payload.model_dump(exclude_none=True))
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
