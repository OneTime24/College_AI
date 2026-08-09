from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.device import DeviceCreate, DeviceRead, DeviceUpdate
from app.services import device_service

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("", response_model=list[DeviceRead])
async def get_devices(db: Session = Depends(get_db)):
    return device_service.list_devices(db)


@router.get("/{device_id}", response_model=DeviceRead)
async def get_device(device_id: int, db: Session = Depends(get_db)):
    device = device_service.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device


@router.post("", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
async def create_device(payload: DeviceCreate, db: Session = Depends(get_db)):
    try:
        return device_service.create_device(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/{device_id}", response_model=DeviceRead)
async def update_device(device_id: int, payload: DeviceUpdate, db: Session = Depends(get_db)):
    device = device_service.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    try:
        return device_service.update_device(db, device, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(device_id: int, db: Session = Depends(get_db)):
    device = device_service.get_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device_service.delete_device(db, device)
