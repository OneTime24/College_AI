from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.room import Room
from app.schemas.room import RoomCreate, RoomUpdate


def list_rooms(db: Session) -> list[Room]:
    return list(db.scalars(select(Room).options(selectinload(Room.devices)).order_by(Room.name)))


def get_room(db: Session, room_id: int) -> Room | None:
    return db.scalar(select(Room).options(selectinload(Room.devices)).where(Room.id == room_id))


def create_room(db: Session, payload: RoomCreate) -> Room:
    room = Room(**payload.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


def update_room(db: Session, room: Room, payload: RoomUpdate) -> Room:
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(room, key, value)
    db.commit()
    db.refresh(room)
    return room


def delete_room(db: Session, room: Room) -> None:
    db.delete(room)
    db.commit()
