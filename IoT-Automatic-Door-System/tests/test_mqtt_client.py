"""
MQTT client tests — validates publish/subscribe logic using a mock broker.
No real broker required; uses unittest.mock to patch paho-mqtt.
"""

import json
import pytest
from unittest.mock import MagicMock, patch, call


# ─── Minimal MQTT publisher mirroring firmware/communication/mqtt_client.ino ──

class DoorMQTTClient:
    """Python equivalent of the ESP32 MQTT client for testability."""

    TOPIC_STATUS    = "door/status"
    TOPIC_EVENT     = "door/event"
    TOPIC_COMMAND   = "door/command"
    TOPIC_HEARTBEAT = "door/heartbeat"

    def __init__(self, broker: str, port: int = 1883):
        self.broker     = broker
        self.port       = port
        self._client    = None
        self.connected  = False
        self._queue     = []
        self.door_state = "CLOSED"
        self._command_handler = None

    def connect(self, client):
        self._client   = client
        self.connected = True
        client.subscribe(self.TOPIC_COMMAND)
        self._drain_queue()

    def publish_event(self, event: str, uid: str, reason: str):
        payload = json.dumps({"event": event, "uid": uid, "reason": reason})
        self._publish(self.TOPIC_EVENT, payload)

    def publish_status(self, state: str, dist_cm: int = -1):
        payload = json.dumps({"state": state, "dist_cm": dist_cm})
        self._publish(self.TOPIC_STATUS, payload)

    def publish_heartbeat(self, uptime_s: int, rssi: int):
        payload = json.dumps({"uptime": uptime_s, "rssi": rssi})
        self._publish(self.TOPIC_HEARTBEAT, payload)

    def on_command(self, handler):
        self._command_handler = handler

    def simulate_incoming(self, topic: str, message: str):
        if topic == self.TOPIC_COMMAND and self._command_handler:
            self._command_handler(message.strip())

    def _publish(self, topic: str, payload: str):
        if self.connected and self._client:
            self._client.publish(topic, payload, retain=True)
        else:
            self._queue.append((topic, payload))

    def _drain_queue(self):
        while self._queue and self._client:
            topic, payload = self._queue.pop(0)
            self._client.publish(topic, payload, retain=True)

    def disconnect(self):
        self.connected = False
        self._client   = None


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_paho():
    return MagicMock()


@pytest.fixture
def client(mock_paho):
    c = DoorMQTTClient("localhost", 1883)
    c.connect(mock_paho)
    return c, mock_paho


# ─── Connection tests ─────────────────────────────────────────────────────────

class TestConnection:
    def test_connect_subscribes_to_command_topic(self, client):
        c, mock = client
        mock.subscribe.assert_called_once_with("door/command")

    def test_connected_flag_set(self, client):
        c, _ = client
        assert c.connected is True

    def test_disconnect_clears_state(self, client):
        c, _ = client
        c.disconnect()
        assert c.connected is False
        assert c._client is None


# ─── Publish tests ────────────────────────────────────────────────────────────

class TestPublish:
    def test_publish_event_correct_topic(self, client):
        c, mock = client
        c.publish_event("ACCESS_GRANTED", "A1B2C3D4", "rfid")
        args = mock.publish.call_args
        assert args[0][0] == "door/event"

    def test_publish_event_valid_json(self, client):
        c, mock = client
        c.publish_event("ACCESS_DENIED", "BADC0FFE", "unauthorized_rfid")
        payload = json.loads(mock.publish.call_args[0][1])
        assert payload["event"]  == "ACCESS_DENIED"
        assert payload["uid"]    == "BADC0FFE"
        assert payload["reason"] == "unauthorized_rfid"

    def test_publish_status_open(self, client):
        c, mock = client
        c.publish_status("OPEN", dist_cm=45)
        payload = json.loads(mock.publish.call_args[0][1])
        assert payload["state"]   == "OPEN"
        assert payload["dist_cm"] == 45

    def test_publish_status_closed(self, client):
        c, mock = client
        c.publish_status("CLOSED")
        payload = json.loads(mock.publish.call_args[0][1])
        assert payload["state"] == "CLOSED"

    def test_publish_heartbeat(self, client):
        c, mock = client
        c.publish_heartbeat(uptime_s=3600, rssi=-65)
        payload = json.loads(mock.publish.call_args[0][1])
        assert payload["uptime"] == 3600
        assert payload["rssi"]   == -65

    def test_all_publishes_use_retain(self, client):
        c, mock = client
        c.publish_event("DOOR_CLOSED", "", "auto_close")
        _, kwargs = mock.publish.call_args
        assert kwargs.get("retain") is True or mock.publish.call_args[0][2] is True

    def test_status_topic(self, client):
        c, mock = client
        c.publish_status("OPEN")
        assert mock.publish.call_args[0][0] == "door/status"

    def test_heartbeat_topic(self, client):
        c, mock = client
        c.publish_heartbeat(100, -70)
        assert mock.publish.call_args[0][0] == "door/heartbeat"


# ─── Offline queue tests ──────────────────────────────────────────────────────

class TestOfflineQueue:
    def test_messages_queued_when_disconnected(self):
        c = DoorMQTTClient("localhost")
        c.publish_event("DOOR_OPENED", "", "rfid")
        c.publish_event("DOOR_CLOSED", "", "auto_close")
        assert len(c._queue) == 2

    def test_queue_drained_on_connect(self):
        c    = DoorMQTTClient("localhost")
        mock = MagicMock()
        c.publish_event("DOOR_OPENED", "", "rfid")
        c.publish_event("ACCESS_GRANTED", "AA", "rfid")
        c.connect(mock)
        # subscribe call + 2 queued publishes
        assert mock.publish.call_count == 2
        assert len(c._queue) == 0

    def test_queue_order_preserved(self):
        c    = DoorMQTTClient("localhost")
        mock = MagicMock()
        c.publish_event("FIRST",  "", "")
        c.publish_event("SECOND", "", "")
        c.connect(mock)
        first_payload  = json.loads(mock.publish.call_args_list[0][0][1])
        second_payload = json.loads(mock.publish.call_args_list[1][0][1])
        assert first_payload["event"]  == "FIRST"
        assert second_payload["event"] == "SECOND"


# ─── Incoming command tests ───────────────────────────────────────────────────

class TestIncomingCommands:
    def test_open_command_triggers_handler(self, client):
        c, _ = client
        handler = MagicMock()
        c.on_command(handler)
        c.simulate_incoming("door/command", "OPEN")
        handler.assert_called_once_with("OPEN")

    def test_close_command_triggers_handler(self, client):
        c, _ = client
        handler = MagicMock()
        c.on_command(handler)
        c.simulate_incoming("door/command", "CLOSE")
        handler.assert_called_once_with("CLOSE")

    def test_status_command_triggers_handler(self, client):
        c, _ = client
        handler = MagicMock()
        c.on_command(handler)
        c.simulate_incoming("door/command", "STATUS")
        handler.assert_called_once_with("STATUS")

    def test_command_with_whitespace_stripped(self, client):
        c, _ = client
        handler = MagicMock()
        c.on_command(handler)
        c.simulate_incoming("door/command", "  OPEN  ")
        handler.assert_called_once_with("OPEN")

    def test_unrelated_topic_ignored(self, client):
        c, _ = client
        handler = MagicMock()
        c.on_command(handler)
        c.simulate_incoming("door/status", "OPEN")
        handler.assert_not_called()

    def test_no_handler_registered_no_crash(self, client):
        c, _ = client
        # should not raise even with no handler set
        c.simulate_incoming("door/command", "OPEN")
