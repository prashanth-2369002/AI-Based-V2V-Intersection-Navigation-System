"""
IoT Automatic Door System — Flask REST API
Subscribes to MQTT events, logs them to SQLite, and exposes an HTTP API.
"""

import os
import json
import sqlite3
import threading
from datetime import datetime, timezone
from flask import Flask, jsonify, request, Response
import paho.mqtt.client as mqtt_lib

app = Flask(__name__)

DB_PATH      = os.getenv("DB_PATH",      "door_events.db")
MQTT_BROKER  = os.getenv("MQTT_BROKER",  "localhost")
MQTT_PORT    = int(os.getenv("MQTT_PORT", 1883))
MQTT_USER    = os.getenv("MQTT_USER",    "")
MQTT_PASS    = os.getenv("MQTT_PASS",    "")
SECRET_KEY   = os.getenv("SECRET_KEY",   "change_me_in_production")

door_state = {"state": "UNKNOWN", "updated_at": None}

# Single persistent connection — required for :memory: in tests and fine for
# single-process production use. check_same_thread=False allows the MQTT
# background thread to write without a threading error.
_db_conn: sqlite3.Connection | None = None
_db_lock = threading.Lock()


# ─── Database ─────────────────────────────────────────────────────────────────

def get_db() -> sqlite3.Connection:
    global _db_conn
    if _db_conn is None:
        _db_conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _db_conn.row_factory = sqlite3.Row
    return _db_conn


def init_db():
    with _db_lock:
        get_db().execute("""
            CREATE TABLE IF NOT EXISTS events (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp  TEXT    NOT NULL,
                event      TEXT    NOT NULL,
                uid        TEXT,
                reason     TEXT,
                raw_json   TEXT
            )
        """)
        get_db().commit()
    print(f"[DB] Initialized at {DB_PATH}")


def log_event(event: str, uid: str, reason: str, raw: str):
    ts = datetime.now(timezone.utc).isoformat()
    with _db_lock:
        get_db().execute(
            "INSERT INTO events (timestamp, event, uid, reason, raw_json) VALUES (?,?,?,?,?)",
            (ts, event, uid, reason, raw)
        )
        get_db().commit()
    print(f"[DB] Logged: {event} uid={uid} reason={reason}")


# ─── MQTT ─────────────────────────────────────────────────────────────────────

def on_message(client, userdata, msg):
    payload = msg.payload.decode("utf-8", errors="replace")
    topic   = msg.topic
    print(f"[MQTT] {topic}: {payload}")

    if topic == "door/event":
        try:
            data = json.loads(payload)
            event  = data.get("event",  "UNKNOWN")
            uid    = data.get("uid",    "")
            reason = data.get("reason", "")
            log_event(event, uid, reason, payload)

            if event in ("DOOR_OPENED", "ACCESS_GRANTED"):
                door_state["state"] = "OPEN"
            elif event == "DOOR_CLOSED":
                door_state["state"] = "CLOSED"
            door_state["updated_at"] = datetime.utcnow().isoformat()
        except json.JSONDecodeError:
            log_event("PARSE_ERROR", "", "", payload)

    elif topic == "door/status":
        try:
            data = json.loads(payload)
            door_state["state"]      = data.get("state", "UNKNOWN")
            door_state["updated_at"] = datetime.utcnow().isoformat()
            door_state.update(data)
        except json.JSONDecodeError:
            pass


def start_mqtt():
    client = mqtt_lib.Client()
    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASS)
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.subscribe([("door/event", 0), ("door/status", 0)])
    client.loop_forever()


# ─── REST API ─────────────────────────────────────────────────────────────────

@app.get("/api/status")
def api_status():
    return jsonify(door_state)


@app.get("/api/logs")
def api_logs():
    limit  = int(request.args.get("limit",  100))
    offset = int(request.args.get("offset",   0))
    event_filter = request.args.get("event")

    with get_db() as conn:
        if event_filter:
            rows = conn.execute(
                "SELECT * FROM events WHERE event=? ORDER BY id DESC LIMIT ? OFFSET ?",
                (event_filter, limit, offset)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM events ORDER BY id DESC LIMIT ? OFFSET ?",
                (limit, offset)
            ).fetchall()

    return jsonify([dict(r) for r in rows])


@app.post("/api/command")
def api_command():
    data = request.get_json(force=True)
    cmd  = data.get("command", "").upper()
    if cmd not in ("OPEN", "CLOSE", "STATUS"):
        return jsonify({"error": "Invalid command. Use OPEN, CLOSE, or STATUS"}), 400

    mqtt_cmd_client = mqtt_lib.Client()
    mqtt_cmd_client.connect(MQTT_BROKER, MQTT_PORT, 5)
    mqtt_cmd_client.publish("door/command", cmd)
    mqtt_cmd_client.disconnect()
    return jsonify({"sent": cmd})


@app.get("/api/logs/export")
def api_export():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM events ORDER BY id").fetchall()

    def generate():
        yield "id,timestamp,event,uid,reason\n"
        for r in rows:
            yield f"{r['id']},{r['timestamp']},{r['event']},{r['uid']},{r['reason']}\n"

    return Response(generate(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=door_events.csv"})


@app.delete("/api/logs/clear")
def api_clear():
    auth = request.headers.get("X-Admin-Key")
    if auth != SECRET_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    with get_db() as conn:
        conn.execute("DELETE FROM events")
    return jsonify({"cleared": True})


@app.get("/api/stats")
def api_stats():
    with get_db() as conn:
        total   = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        granted = conn.execute("SELECT COUNT(*) FROM events WHERE event='ACCESS_GRANTED'").fetchone()[0]
        denied  = conn.execute("SELECT COUNT(*) FROM events WHERE event='ACCESS_DENIED'").fetchone()[0]
        opens   = conn.execute("SELECT COUNT(*) FROM events WHERE event='DOOR_OPENED'").fetchone()[0]
    return jsonify({
        "total_events":    total,
        "access_granted":  granted,
        "access_denied":   denied,
        "door_opens":      opens,
        "deny_rate":       round(denied / (granted + denied) * 100, 1) if (granted + denied) else 0
    })


# ─── Entry Point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    mqtt_thread = threading.Thread(target=start_mqtt, daemon=True)
    mqtt_thread.start()
    print(f"[SERVER] Starting on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
