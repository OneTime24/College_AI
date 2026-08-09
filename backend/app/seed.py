from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.device import Device
from app.models.event import Event
from app.models.room import Room
from app.models.user import User


def seed_database(db: Session) -> None:
    """Create clearly labelled demonstration records once, for local development."""
    if db.scalar(select(Room.id).limit(1)):
        return
    rooms = [
        Room(name="Main Entrance", description="Primary campus arrival and reception area.", building="Main Block", floor="Ground", room_number="ENT-01", room_type="Entrance", temperature=25.1, humidity=49.0, occupancy=18, active_mode="Monitoring"),
        Room(name="AI Lab", description="Demonstration and applied artificial intelligence laboratory.", building="Technology Block", floor="1", room_number="AI-101", room_type="Laboratory", temperature=22.5, humidity=44.0, occupancy=12, active_mode="Teaching"),
        Room(name="Physics Lab", description="Experimental physics teaching laboratory.", building="Science Block", floor="1", room_number="PHY-104", room_type="Laboratory", temperature=23.7, humidity=47.0, occupancy=8, active_mode="Teaching"),
        Room(name="Computer Lab", description="Open-access computing laboratory.", building="Technology Block", floor="2", room_number="CS-204", room_type="Laboratory", temperature=21.9, humidity=42.0, occupancy=26, active_mode="Active"),
        Room(name="Principal Office", description="College administration office.", building="Administration Block", floor="1", room_number="ADM-101", room_type="Office", temperature=23.0, humidity=45.0, occupancy=2, active_mode="Available"),
        Room(name="Main Hall", description="College events, lectures, and assemblies.", building="Main Block", floor="Ground", room_number="HALL-01", room_type="Hall", temperature=24.2, humidity=48.0, occupancy=75, active_mode="Event Ready"),
    ]
    db.add_all(rooms)
    db.flush()
    by_name = {room.name: room for room in rooms}
    devices = [
        *(Device(name=name, device_type=device_type, room_id=by_name["AI Lab"].id, status=status, is_online=True, metadata_={"source": "demo_simulation"}) for name, device_type, status in [("Main Lights", "Lighting", "on"), ("Fan", "Ventilation", "standby"), ("Curtains", "Window Covering", "closed"), ("RGB LEDs", "Ambient Lighting", "on"), ("Temperature Sensor", "Sensor", "reporting")]),
        *(Device(name=name, device_type=device_type, room_id=by_name["Computer Lab"].id, status=status, is_online=True, metadata_={"source": "demo_simulation"}) for name, device_type, status in [("Main Lights", "Lighting", "on"), ("AC", "Climate Control", "cooling"), ("Projector", "Display", "standby")]),
        *(Device(name=name, device_type=device_type, room_id=by_name["Physics Lab"].id, status=status, is_online=True, metadata_={"source": "demo_simulation"}) for name, device_type, status in [("Main Lights", "Lighting", "on"), ("Fan", "Ventilation", "on"), ("Temperature Sensor", "Sensor", "reporting")]),
    ]
    db.add_all(devices)
    now = datetime.now()
    db.add_all([
        Event(event_type="movement", location="Main Entrance", description="Demonstration entry movement recorded by simulated reception sensor.", timestamp=now - timedelta(minutes=4), metadata_={"demo": True}),
        Event(event_type="device", location="AI Lab", description="Main Lights status updated to on (simulation).", timestamp=now - timedelta(minutes=12), metadata_={"demo": True}),
        Event(event_type="sensor", location="Computer Lab", description="Temperature reading received: 21.9°C (simulation).", timestamp=now - timedelta(minutes=26), metadata_={"demo": True}),
        Event(event_type="system", location="Main Hall", description="Dashboard demonstration data initialized.", timestamp=now - timedelta(hours=1), metadata_={"demo": True}),
    ])
    db.add(User(username="admin", display_name="College Administrator", role="admin", is_active=True))
    db.commit()
