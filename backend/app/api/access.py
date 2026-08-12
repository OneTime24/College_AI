from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.config import Settings, get_settings

router = APIRouter(prefix="/access", tags=["access"])


def require_dashboard_access(
    x_dashboard_key: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    if settings.dashboard_access_key and x_dashboard_key != settings.dashboard_access_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Dashboard access key is required.")


@router.get("/dashboard")
async def dashboard_access(_: None = Depends(require_dashboard_access)):
    return {"allowed": True}
