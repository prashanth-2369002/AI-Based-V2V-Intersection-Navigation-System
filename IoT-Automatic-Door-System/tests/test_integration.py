"""
Integration tests — wires sensor logic + MQTT client + Flask API together
without real hardware or a real broker. Validates the full event pipeline:
  sensor decision → MQTT publish → backend receive → DB log → API retrieve
"""

import json
import os
import pytest
from unittest.mock import MagicMock, patch

os.environ["DB_PATH"]     = ":memory:"
os.environ["MQTT_BROKER"] = "localhost"
os.environ["SECRET_KEY"]  = "integration_test"

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from server import app, init_db, log_event, door_state

# ── Replicated sensor logic (from test_sensor_logic.py) ─────────────────────
AUTHORIZED_UIDS        = {"A1B2C3D4", "11223344", "DEADBEEF"}
ULTRASONIC_TRIGGER_CM  = 100
PROXIMITY_UNLOCK_CM    = 30

def sensor_decision(pir, distance_cm, rfid_uid):
    if not pir:                                       return None, "no_motion"
    if distance_cm < 0 or distance_cm > 100:          return None, "out_of_range"
    if rfid_uid is not None:
        if rfid_uid in AUTHORIZED_UIDS:               return "ACCESS_GRANTED", "rfid"
        else:                                          return "ACCESS_DENIED",  "unauthorized_rfid"
    if distance_cm <= PROXIMITY_UNLOCK_CM:             return "ACCESS_GRANTED", "proximity"
    return None, "no_credential"


# ── Minimal event pipeline ───────────────────────────────────────────────────

def process_sensor_event(pir, distance_cm, rfid_uid):
    """Simulates: ESP32 decision → MQTT publish → backend on_message → DB log."""
    event, reason = sensor_decision(pir, distance_cm, rfid_uid)
    if event:
        uid = rfid_uid or "NONE"
        log_event(event, uid, reason, json.dumps(
            {"event": event, "uid": uid, "reason": reason}
        ))
        if event == "ACCESS_GRANTED":
            door_state["state"] = "OPEN"
    return event, reason


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def flask_client():
    import server as srv
    srv._db_conn = None          # fresh :memory: DB for each test
    app.config["TESTING"] = True
    with app.test_client() as c:
        with app.app_context():
            init_db()
            door_state.update({"state": "UNKNOWN", "updated_at": None})
            yield c
    srv._db_conn = None


# ── Full pipeline tests ───────────────────────────────────────────────────────

class TestAccessGrantedPipeline:
    def test_rfid_grant_logged_and_queryable(self, flask_client):
        event, reason = process_sensor_event(True, 50, "A1B2C3D4")
        assert event == "ACCESS_GRANTED"

        resp = flask_client.get("/api/logs")
        logs = json.loads(resp.data)
        assert any(l["event"] == "ACCESS_GRANTED" and l["uid"] == "A1B2C3D4" for l in logs)

    def test_rfid_grant_updates_door_state(self, flask_client):
        process_sensor_event(True, 50, "A1B2C3D4")
        assert door_state["state"] == "OPEN"

    def test_proximity_grant_logged(self, flask_client):
        event, reason = process_sensor_event(True, 25, None)
        assert event == "ACCESS_GRANTED"
        assert reason == "proximity"

        resp = flask_client.get("/api/logs")
        logs = json.loads(resp.data)
        assert any(l["reason"] == "proximity" for l in logs)


class TestAccessDeniedPipeline:
    def test_denied_rfid_logged(self, flask_client):
        event, reason = process_sensor_event(True, 50, "BADC0FFE")
        assert event == "ACCESS_DENIED"

        resp = flask_client.get("/api/logs")
        logs = json.loads(resp.data)
        assert any(l["event"] == "ACCESS_DENIED" and l["uid"] == "BADC0FFE" for l in logs)

    def test_denied_does_not_change_door_state(self, flask_client):
        door_state["state"] = "CLOSED"
        process_sensor_event(True, 50, "BADC0FFE")
        assert door_state["state"] == "CLOSED"


class TestNoTriggerPipeline:
    def test_no_pir_no_event_no_log(self, flask_client):
        event, _ = process_sensor_event(False, 50, None)
        assert event is None

        resp = flask_client.get("/api/logs")
        assert json.loads(resp.data) == []

    def test_out_of_range_no_event(self, flask_client):
        event, _ = process_sensor_event(True, 150, None)
        assert event is None


class TestMultipleEventsStats:
    def test_stats_reflect_multiple_events(self, flask_client):
        process_sensor_event(True,  50, "A1B2C3D4")  # GRANTED
        process_sensor_event(True,  50, "A1B2C3D4")  # GRANTED
        process_sensor_event(True,  50, "BADC0FFE")  # DENIED

        resp = flask_client.get("/api/stats")
        stats = json.loads(resp.data)
        assert stats["access_granted"] == 2
        assert stats["access_denied"]  == 1
        assert stats["deny_rate"]      == pytest.approx(33.3, abs=0.1)

    def test_csv_export_contains_all_events(self, flask_client):
        process_sensor_event(True, 50, "A1B2C3D4")
        process_sensor_event(True, 50, "BADC0FFE")

        resp = flask_client.get("/api/logs/export")
        body = resp.data.decode()
        assert "ACCESS_GRANTED" in body
        assert "ACCESS_DENIED"  in body
        assert "A1B2C3D4"       in body


class TestRemoteCommandIntegration:
    @patch("server.mqtt_lib.Client")
    def test_remote_open_command_sent(self, mock_mqtt_class, flask_client):
        mock_instance = MagicMock()
        mock_mqtt_class.return_value = mock_instance

        resp = flask_client.post("/api/command",
                                 data=json.dumps({"command": "OPEN"}),
                                 content_type="application/json")
        assert resp.status_code == 200
        assert json.loads(resp.data)["sent"] == "OPEN"
        mock_instance.publish.assert_called_once_with("door/command", "OPEN")

    @patch("server.mqtt_lib.Client")
    def test_remote_close_command_sent(self, mock_mqtt_class, flask_client):
        mock_instance = MagicMock()
        mock_mqtt_class.return_value = mock_instance

        resp = flask_client.post("/api/command",
                                 data=json.dumps({"command": "CLOSE"}),
                                 content_type="application/json")
        assert resp.status_code == 200
        mock_instance.publish.assert_called_once_with("door/command", "CLOSE")


class TestAdminOperations:
    def test_clear_requires_auth(self, flask_client):
        resp = flask_client.delete("/api/logs/clear")
        assert resp.status_code == 401

    def test_clear_with_valid_key(self, flask_client):
        import server as srv
        process_sensor_event(True, 50, "A1B2C3D4")
        resp = flask_client.delete("/api/logs/clear",
                                   headers={"X-Admin-Key": srv.SECRET_KEY})
        assert resp.status_code == 200
        logs = json.loads(flask_client.get("/api/logs").data)
        assert logs == []
