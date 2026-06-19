"""
Smart EV Charging System — Dashboard Backend
Flask + Flask-MQTT + SQLAlchemy + SQLite
"""
from __future__ import annotations

import json
import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from flask_mqtt import Mqtt
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///ev_charging.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MQTT_BROKER_URL"] = os.getenv("MQTT_BROKER", "127.0.0.1")
app.config["MQTT_BROKER_PORT"] = int(os.getenv("MQTT_PORT", "1883"))
app.config["MQTT_KEEPALIVE"] = 60

db = SQLAlchemy(app)
mqtt = Mqtt(app)

UNIT_RATE = float(os.getenv("UNIT_RATE_RS", "8.0"))

# ─── Models ───────────────────────────────────────────────────────────────────

class Telemetry(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow)
    uid         = db.Column(db.String(16))
    voltage     = db.Column(db.Float)
    current_a   = db.Column(db.Float)
    power_w     = db.Column(db.Float)
    energy_wh   = db.Column(db.Float)
    soc         = db.Column(db.Float)
    temp_c      = db.Column(db.Float)
    elapsed_s   = db.Column(db.Integer)


class SessionLog(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    uid         = db.Column(db.String(16))
    event       = db.Column(db.String(32))
    energy_wh   = db.Column(db.Float, nullable=True)
    cost_rs     = db.Column(db.Float, nullable=True)
    duration_s  = db.Column(db.Integer, nullable=True)
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow)


# ─── MQTT handlers ────────────────────────────────────────────────────────────

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe("ev/telemetry")
    mqtt.subscribe("ev/session")
    mqtt.subscribe("ev/fault")
    print(f"[MQTT] Connected (rc={rc}), subscribed to ev/#")


@mqtt.on_message()
def handle_message(client, userdata, message):
    topic   = message.topic
    payload = message.payload.decode("utf-8", errors="replace")

    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        print(f"[MQTT] Bad JSON on {topic}: {payload}")
        return

    with app.app_context():
        if topic == "ev/telemetry":
            row = Telemetry(
                uid       = data.get("uid", ""),
                voltage   = float(data.get("voltage", 0)),
                current_a = float(data.get("current", 0)),
                power_w   = float(data.get("power_w", 0)),
                energy_wh = float(data.get("energy_wh", 0)),
                soc       = float(data.get("soc", 0)),
                temp_c    = float(data.get("temp_c", 0)),
                elapsed_s = int(data.get("elapsed_s", 0)),
            )
            db.session.add(row)
            db.session.commit()

        elif topic in ("ev/session", "ev/fault"):
            row = SessionLog(
                uid        = data.get("uid", ""),
                event      = data.get("event", topic.split("/")[-1]),
                energy_wh  = float(data["energy_wh"]) if "energy_wh" in data else None,
                cost_rs    = float(data["cost_rs"])   if "cost_rs"   in data else None,
                duration_s = int(data["duration_s"])  if "duration_s" in data else None,
            )
            db.session.add(row)
            db.session.commit()


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def index():
    return render_template("index.html", unit_rate=UNIT_RATE)


@app.get("/api/live")
def api_live():
    """Last telemetry reading."""
    row = Telemetry.query.order_by(Telemetry.id.desc()).first()
    if not row:
        return jsonify({"status": "no_data"})
    return jsonify({
        "uid":       row.uid,
        "voltage":   row.voltage,
        "current":   row.current_a,
        "power_w":   row.power_w,
        "energy_wh": row.energy_wh,
        "soc":       row.soc,
        "temp_c":    row.temp_c,
        "elapsed_s": row.elapsed_s,
        "timestamp": row.timestamp.isoformat(),
    })


@app.get("/api/history")
def api_history():
    """Last 100 telemetry points for graphing."""
    rows = (Telemetry.query
            .order_by(Telemetry.id.desc())
            .limit(100)
            .all())
    rows.reverse()
    return jsonify([{
        "t":       r.timestamp.strftime("%H:%M:%S"),
        "soc":     r.soc,
        "power":   r.power_w,
        "temp":    r.temp_c,
        "voltage": r.voltage,
    } for r in rows])


@app.get("/api/sessions")
def api_sessions():
    """Session start/end log."""
    rows = (SessionLog.query
            .filter(SessionLog.event.in_(["session_end", "fault"]))
            .order_by(SessionLog.id.desc())
            .limit(50)
            .all())
    return jsonify([{
        "uid":        r.uid,
        "event":      r.event,
        "energy_wh":  r.energy_wh,
        "cost_rs":    r.cost_rs,
        "duration_s": r.duration_s,
        "timestamp":  r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
    } for r in rows])


@app.get("/api/stats")
def api_stats():
    """Aggregate stats for the summary cards."""
    total_sessions = SessionLog.query.filter_by(event="session_end").count()
    total_energy   = db.session.query(
        db.func.sum(SessionLog.energy_wh)
    ).filter_by(event="session_end").scalar() or 0.0
    total_revenue  = db.session.query(
        db.func.sum(SessionLog.cost_rs)
    ).filter_by(event="session_end").scalar() or 0.0
    fault_count    = SessionLog.query.filter_by(event="fault").count()

    return jsonify({
        "total_sessions": total_sessions,
        "total_energy_wh": round(total_energy, 2),
        "total_revenue_rs": round(total_revenue, 2),
        "fault_count": fault_count,
    })


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=False)
