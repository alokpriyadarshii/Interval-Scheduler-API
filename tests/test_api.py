from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from smart_scheduler.api import create_app


def test_api_schedule_roundtrip() -> None:
    app = create_app()
    client = TestClient(app)

    tz = timezone.utc
    base = datetime(2026, 1, 16, tzinfo=tz)

    payloads = [
        {
            "task_id": "T1",
            "start": (base + timedelta(hours=1)).isoformat(),
            "end": (base + timedelta(hours=3)).isoformat(),
            "priority": 5,
        },
        {
            "task_id": "T2",
            "start": (base + timedelta(hours=2)).isoformat(),
            "end": (base + timedelta(hours=5)).isoformat(),
            "priority": 6,
        },
        {
            "task_id": "T5",
            "start": (base + timedelta(hours=5)).isoformat(),
            "end": (base + timedelta(hours=8)).isoformat(),
            "priority": 11,
        },
    ]

    for p in payloads:
        r = client.post("/tasks", json=p)
        assert r.status_code == 200

    r = client.post("/schedule")
    assert r.status_code == 200
    data = r.json()
    assert "total_priority" in data
    assert data["total_priority"] >= 11
    assert all("task_id" in t for t in data["tasks"])
    

def test_api_rejects_naive_datetimes() -> None:
    app = create_app()
    client = TestClient(app)

    payload = {
        "task_id": "N1",
        "start": "2026-01-16T10:00:00",
        "end": "2026-01-16T11:00:00",
        "priority": 3,
    }

    response = client.post("/tasks", json=payload)
    assert response.status_code == 400
    assert "timezone-aware" in response.json()["detail"]
