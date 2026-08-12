from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.access import require_dashboard_access
from app.schemas.event import EventCreate, EventRead
from app.services import event_service

router = APIRouter(prefix="/events", tags=["events"], dependencies=[Depends(require_dashboard_access)])


@router.get("", response_model=list[EventRead])
async def get_events(
    limit: int = Query(default=50, ge=1, le=200),
    location: str | None = None,
    event_type: str | None = None,
    db: Session = Depends(get_db),
):
    return event_service.list_events(db, limit, location, event_type)


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
async def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    return event_service.create_event(db, payload)
