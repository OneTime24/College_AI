from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.api.access import require_dashboard_access
from app.models.device import Device
from app.models.event import Event
from app.models.room import Room
from app.schemas.system import SystemStatus
from app.services.ai_service import get_ai_service

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/status", response_model=SystemStatus, dependencies=[Depends(require_dashboard_access)])
async def system_status(db: Session = Depends(get_db)):
    ai = await get_ai_service().status()
    return SystemStatus(
        backend="online",
        database="online",
        llm=ai.status,
        rooms=db.scalar(select(func.count()).select_from(Room)) or 0,
        devices=db.scalar(select(func.count()).select_from(Device)) or 0,
        recent_events=db.scalar(select(func.count()).select_from(Event)) or 0,
    )
