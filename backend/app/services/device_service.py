from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.device import Device
from app.models.room import Room
from app.schemas.device import DeviceCreate, DeviceUpdate


def list_devices(db: Session) -> list[Device]:
    return list(db.scalars(select(Device).options(joinedload(Device.room)).order_by(Device.name)))


def get_device(db: Session, device_id: int) -> Device | None:
    return db.scalar(select(Device).options(joinedload(Device.room)).where(Device.id == device_id))


def create_device(db: Session, payload: DeviceCreate) -> Device:
    if not db.get(Room, payload.room_id):
        raise ValueError("Room not found")
    device = Device(**payload.model_dump())
    db.add(device)
    db.commit()
    db.refresh(device)
    return device


def update_device(db: Session, device: Device, payload: DeviceUpdate) -> Device:
    data = payload.model_dump(exclude_unset=True)
    if "room_id" in data and not db.get(Room, data["room_id"]):
        raise ValueError("Room not found")
    for key, value in data.items():
        setattr(device, key, value)
    db.commit()
    db.refresh(device)
    return device


def delete_device(db: Session, device: Device) -> None:
    db.delete(device)
    db.commit()
