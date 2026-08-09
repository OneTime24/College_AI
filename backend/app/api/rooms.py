from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.room import RoomCreate, RoomDetail, RoomRead, RoomUpdate
from app.services import room_service

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=list[RoomDetail])
async def get_rooms(db: Session = Depends(get_db)):
    return room_service.list_rooms(db)


@router.get("/{room_id}", response_model=RoomDetail)
async def get_room(room_id: int, db: Session = Depends(get_db)):
    room = room_service.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room


@router.post("", response_model=RoomRead, status_code=status.HTTP_201_CREATED)
async def create_room(payload: RoomCreate, db: Session = Depends(get_db)):
    return room_service.create_room(db, payload)


@router.put("/{room_id}", response_model=RoomRead)
async def update_room(room_id: int, payload: RoomUpdate, db: Session = Depends(get_db)):
    room = room_service.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room_service.update_room(db, room, payload)


@router.delete("/{room_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_room(room_id: int, db: Session = Depends(get_db)):
    room = room_service.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    room_service.delete_room(db, room)
