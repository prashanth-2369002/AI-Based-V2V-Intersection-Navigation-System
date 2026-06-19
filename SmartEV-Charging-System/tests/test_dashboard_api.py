"""
Flask API integration tests for the dashboard backend.
Uses pytest-flask test client — no real MQTT broker or hardware needed.
"""
import json
import sys
import os
import pytest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'software', 'dashboard'))

from app import app as flask_app, db, Telemetry, SessionLog


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def app():
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    # Disable flask-mqtt in test mode to avoid needing a real broker
    flask_app.config["MQTT_BROKER_URL"] = "127.0.0.1"
    flask_app.config["MQTT_BROKER_PORT"] = 1883
    return flask_app


@pytest.fixture(scope="session")
def client(app):
    with app.app_context():
        db.create_all()
        _seed_test_data(app)
    return app.test_client()


def _seed_test_data(app):
    """Insert known rows so API assertions are deterministic."""
    with app.app_context():
        base_time = datetime(2025, 6, 1, 10, 0, 0)

        # 5 telemetry readings
        for i in range(5):
            db.session.add(Telemetry(
                timestamp = base_time + timedelta(seconds=i * 5),
                uid       = "A1B2C3D4",
                voltage   = 11.8 + i * 0.05,
                current_a = 0.80 + i * 0.02,
                power_w   = 9.5  + i * 0.1,
                energy_wh = i * 0.05,
                soc       = 60.0 + i * 2.0,
                temp_c    = 30.0 + i * 0.5,
                elapsed_s = i * 5,
            ))

        # 2 completed sessions
        db.session.add(SessionLog(
            uid        = "A1B2C3D4",
            event      = "session_end",
            energy_wh  = 230.5,
            cost_rs    = 1.84,
            duration_s = 1380,
            timestamp  = base_time,
        ))
        db.session.add(SessionLog(
            uid        = "F4E3D2C1",
            event      = "session_end",
            energy_wh  = 455.0,
            cost_rs    = 3.64,
            duration_s = 2700,
            timestamp  = base_time + timedelta(hours=2),
        ))

        # 1 fault event
        db.session.add(SessionLog(
            uid       = "A1B2C3D4",
            event     = "fault",
            timestamp = base_time + timedelta(hours=1),
        ))

        db.session.commit()


# ─── Index route ──────────────────────────────────────────────────────────────

class TestIndexRoute:
    def test_returns_200(self, client):
        r = client.get("/")
        assert r.status_code == 200

    def test_returns_html(self, client):
        r = client.get("/")
        assert b"Smart EV" in r.data or b"<!DOCTYPE" in r.data


# ─── /api/live ────────────────────────────────────────────────────────────────

class TestApiLive:
    def test_returns_200(self, client):
        r = client.get("/api/live")
        assert r.status_code == 200

    def test_returns_json(self, client):
        r = client.get("/api/live")
        data = json.loads(r.data)
        assert isinstance(data, dict)

    def test_has_required_keys(self, client):
        r    = client.get("/api/live")
        data = json.loads(r.data)
        if data.get("status") == "no_data":
            pytest.skip("No data seeded — check fixture")
        for key in ("uid", "voltage", "current", "power_w", "energy_wh", "soc", "temp_c", "elapsed_s"):
            assert key in data, f"Missing key: {key}"

    def test_soc_in_valid_range(self, client):
        r    = client.get("/api/live")
        data = json.loads(r.data)
        if "soc" in data:
            assert 0.0 <= data["soc"] <= 100.0

    def test_voltage_positive(self, client):
        r    = client.get("/api/live")
        data = json.loads(r.data)
        if "voltage" in data:
            assert data["voltage"] > 0


# ─── /api/history ─────────────────────────────────────────────────────────────

class TestApiHistory:
    def test_returns_list(self, client):
        r    = client.get("/api/history")
        data = json.loads(r.data)
        assert isinstance(data, list)

    def test_each_item_has_chart_keys(self, client):
        r    = client.get("/api/history")
        rows = json.loads(r.data)
        if not rows:
            pytest.skip("No history data")
        for row in rows:
            for key in ("t", "soc", "power", "temp", "voltage"):
                assert key in row, f"Missing key: {key}"

    def test_max_100_points(self, client):
        r    = client.get("/api/history")
        rows = json.loads(r.data)
        assert len(rows) <= 100


# ─── /api/sessions ────────────────────────────────────────────────────────────

class TestApiSessions:
    def test_returns_list(self, client):
        r    = client.get("/api/sessions")
        data = json.loads(r.data)
        assert isinstance(data, list)

    def test_session_has_required_keys(self, client):
        r    = client.get("/api/sessions")
        rows = json.loads(r.data)
        if not rows:
            pytest.skip("No session data")
        for row in rows:
            for key in ("uid", "event", "timestamp"):
                assert key in row, f"Missing key: {key}"

    def test_only_end_and_fault_events(self, client):
        r    = client.get("/api/sessions")
        rows = json.loads(r.data)
        for row in rows:
            assert row["event"] in ("session_end", "fault"), (
                f"Unexpected event type: {row['event']}"
            )

    def test_max_50_rows(self, client):
        r    = client.get("/api/sessions")
        rows = json.loads(r.data)
        assert len(rows) <= 50


# ─── /api/stats ───────────────────────────────────────────────────────────────

class TestApiStats:
    def test_returns_200(self, client):
        r = client.get("/api/stats")
        assert r.status_code == 200

    def test_has_required_keys(self, client):
        r    = client.get("/api/stats")
        data = json.loads(r.data)
        for key in ("total_sessions", "total_energy_wh", "total_revenue_rs", "fault_count"):
            assert key in data, f"Missing key: {key}"

    def test_total_sessions_count(self, client):
        r    = client.get("/api/stats")
        data = json.loads(r.data)
        assert data["total_sessions"] == 2   # seeded 2 session_end rows

    def test_fault_count(self, client):
        r    = client.get("/api/stats")
        data = json.loads(r.data)
        assert data["fault_count"] == 1      # seeded 1 fault row

    def test_total_energy_is_sum(self, client):
        r    = client.get("/api/stats")
        data = json.loads(r.data)
        # 230.5 + 455.0 = 685.5 Wh
        assert abs(data["total_energy_wh"] - 685.5) < 0.01

    def test_total_revenue_is_sum(self, client):
        r    = client.get("/api/stats")
        data = json.loads(r.data)
        # 1.84 + 3.64 = 5.48 ₹
        assert abs(data["total_revenue_rs"] - 5.48) < 0.01

    def test_numeric_types(self, client):
        r    = client.get("/api/stats")
        data = json.loads(r.data)
        assert isinstance(data["total_sessions"],   int)
        assert isinstance(data["total_energy_wh"],  float)
        assert isinstance(data["total_revenue_rs"], float)
        assert isinstance(data["fault_count"],      int)
