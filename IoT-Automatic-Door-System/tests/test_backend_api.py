"""
Flask API tests — uses an in-memory SQLite database.
Run: pytest tests/test_backend_api.py -v
"""

import json
import os
import pytest

os.environ["DB_PATH"]     = ":memory:"
os.environ["MQTT_BROKER"] = "localhost"
os.environ["SECRET_KEY"]  = "test_secret"

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from server import app, init_db, log_event


@pytest.fixture
def client():
    import server as srv
    # Reset the shared connection so each test gets a fresh :memory: DB
    srv._db_conn = None
    app.config["TESTING"] = True
    with app.test_client() as c:
        with app.app_context():
            init_db()
            yield c
    srv._db_conn = None


def test_status_endpoint(client):
    resp = client.get("/api/status")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert "state" in data


def test_logs_empty(client):
    resp = client.get("/api/logs")
    assert resp.status_code == 200
    assert json.loads(resp.data) == []


def test_log_event_and_retrieve(client):
    with app.app_context():
        log_event("ACCESS_GRANTED", "A1B2C3D4", "rfid", "{}")
        log_event("ACCESS_DENIED",  "BADC0FFE", "unauthorized_rfid", "{}")

    resp = client.get("/api/logs")
    data = json.loads(resp.data)
    assert len(data) == 2
    assert data[0]["event"] == "ACCESS_DENIED"   # descending order


def test_logs_filter_by_event(client):
    with app.app_context():
        log_event("ACCESS_GRANTED", "A1", "rfid", "{}")
        log_event("DOOR_OPENED",    "",   "rfid", "{}")

    resp = client.get("/api/logs?event=ACCESS_GRANTED")
    data = json.loads(resp.data)
    assert all(r["event"] == "ACCESS_GRANTED" for r in data)


def test_logs_pagination(client):
    with app.app_context():
        for i in range(5):
            log_event("DOOR_OPENED", "", "test", "{}")

    resp = client.get("/api/logs?limit=2&offset=0")
    assert len(json.loads(resp.data)) == 2


def test_command_invalid(client):
    resp = client.post("/api/command",
                       data=json.dumps({"command": "EXPLODE"}),
                       content_type="application/json")
    assert resp.status_code == 400


def test_clear_logs_unauthorized(client):
    resp = client.delete("/api/logs/clear")
    assert resp.status_code == 401


def test_clear_logs_authorized(client):
    with app.app_context():
        log_event("TEST", "", "", "{}")
    resp = client.delete("/api/logs/clear",
                         headers={"X-Admin-Key": "test_secret"})
    assert resp.status_code == 200

    resp2 = client.get("/api/logs")
    assert json.loads(resp2.data) == []


def test_stats_endpoint(client):
    with app.app_context():
        log_event("ACCESS_GRANTED", "A1", "rfid", "{}")
        log_event("ACCESS_DENIED",  "XX", "unauthorized_rfid", "{}")

    resp = client.get("/api/stats")
    data = json.loads(resp.data)
    assert data["access_granted"] == 1
    assert data["access_denied"]  == 1
    assert data["deny_rate"]      == 50.0


def test_export_csv(client):
    with app.app_context():
        log_event("DOOR_OPENED", "", "test", "{}")

    resp = client.get("/api/logs/export")
    assert resp.status_code == 200
    assert b"timestamp" in resp.data
    assert b"DOOR_OPENED" in resp.data
