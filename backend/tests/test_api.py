import pytest


@pytest.mark.anyio
async def test_health_endpoint(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


@pytest.mark.anyio
async def test_database_initialization_seeds_demo_data(client):
    response = await client.get("/api/rooms")
    assert response.status_code == 200
    assert len(response.json()) == 6


@pytest.mark.anyio
async def test_room_creation_and_retrieval(client):
    payload = {"name": "Innovation Studio", "description": "Test room", "building": "Technology Block", "floor": "3", "room_number": "IN-301", "room_type": "Studio", "temperature": 22.0, "humidity": 40.0, "occupancy": 0, "active_mode": "Available"}
    created = await client.post("/api/rooms", json=payload)
    assert created.status_code == 201
    room_id = created.json()["id"]
    fetched = await client.get(f"/api/rooms/{room_id}")
    assert fetched.status_code == 200
    assert fetched.json()["name"] == "Innovation Studio"


@pytest.mark.anyio
async def test_device_retrieval(client):
    response = await client.get("/api/devices")
    assert response.status_code == 200
    devices = response.json()
    assert len(devices) == 11
    assert devices[0]["name"]


@pytest.mark.anyio
async def test_event_creation(client):
    response = await client.post("/api/events", json={"event_type": "system", "location": "AI Lab", "description": "Test event created."})
    assert response.status_code == 201
    assert response.json()["location"] == "AI Lab"


@pytest.mark.anyio
async def test_system_status(client):
    response = await client.get("/api/system/status")
    assert response.status_code == 200
    data = response.json()
    assert data["backend"] == "online"
    assert data["database"] == "online"
    assert data["llm"] in {"offline", "online", "error", "not_configured"}
    assert data["rooms"] == 6
    assert data["devices"] == 11
