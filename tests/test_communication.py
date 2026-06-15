"""
Unit tests for V2V and V2I communication modules (communication.py)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import patch
from communication import (
    CommunicationChannel, Message, MessageType,
    V2VCommunication, V2ICommunication,
)
import config


def _make_message(sender="V1", receiver="V2", msg_type=MessageType.VEHICLE_INFO,
                  payload=None) -> Message:
    return Message(
        sender_id=sender,
        receiver_id=receiver,
        message_type=msg_type,
        timestamp=0.0,
        payload=payload or {},
        sequence_number=0,
        priority=1,
    )


class TestCommunicationChannel:

    def setup_method(self):
        self.channel = CommunicationChannel("test", range_meters=500, delay_ms=50)

    def test_message_delivered_within_range(self):
        msg = _make_message()
        with patch("random.random", return_value=0.5):  # no packet loss
            result = self.channel.send_message(msg, current_time=0.0, distance=100)
        assert result is True

    def test_message_dropped_out_of_range(self):
        msg = _make_message()
        result = self.channel.send_message(msg, current_time=0.0, distance=600)
        assert result is False

    def test_message_not_delivered_before_delay(self):
        msg = _make_message(receiver="V2")
        with patch("random.random", return_value=0.5):
            self.channel.send_message(msg, current_time=0.0, distance=0)
        # Delay = 50 ms → delivery_time = 0.05 s; check at t=0.0
        delivered = self.channel.get_messages_for("V2", current_time=0.0)
        assert len(delivered) == 0

    def test_message_delivered_after_delay(self):
        msg = _make_message(receiver="V2")
        with patch("random.random", return_value=0.5):
            self.channel.send_message(msg, current_time=0.0, distance=0)
        delivered = self.channel.get_messages_for("V2", current_time=1.0)
        assert len(delivered) == 1

    def test_recipient_isolation_wrong_receiver_gets_nothing(self):
        msg = _make_message(receiver="V2")
        with patch("random.random", return_value=0.5):
            self.channel.send_message(msg, current_time=0.0, distance=0)
        # V3 should not get V2's message
        delivered = self.channel.get_messages_for("V3", current_time=1.0)
        assert len(delivered) == 0
        # V2's message must still be available
        delivered_v2 = self.channel.get_messages_for("V2", current_time=1.0)
        assert len(delivered_v2) == 1

    def test_no_misrouted_deliveries(self):
        for receiver in ("V1", "V2", "V3"):
            msg = _make_message(receiver=receiver)
            with patch("random.random", return_value=0.5):
                self.channel.send_message(msg, current_time=0.0, distance=0)
        self.channel.get_messages_for("V1", current_time=1.0)
        self.channel.get_messages_for("V2", current_time=1.0)
        self.channel.get_messages_for("V3", current_time=1.0)
        assert self.channel.misrouted_deliveries == 0

    def test_statistics_contains_expected_keys(self):
        stats = self.channel.get_statistics()
        for key in ("channel_name", "total_messages_sent", "total_messages_received",
                    "message_loss_rate", "pending_messages"):
            assert key in stats

    def test_packet_loss_simulated(self):
        msg = _make_message()
        with patch("random.random", return_value=0.0):  # always loses (0.0 < 0.02)
            result = self.channel.send_message(msg, current_time=0.0, distance=0)
        assert result is False


class TestV2VCommunication:

    def setup_method(self):
        self.v2v = V2VCommunication()
        # Keep vehicles within V2V_RANGE (300 px) so messages are not range-dropped
        self.v2v.register_vehicle("V1", (300, 500))
        self.v2v.register_vehicle("V2", (500, 500))

    def test_broadcast_sends_to_others(self):
        vehicle_data = {"vehicle_id": "V1", "position": (300, 500), "velocity": 20.0,
                        "direction": (1, 0), "vehicle_type": "regular",
                        "state": "approaching", "eta_to_intersection": 5.0,
                        "timestamp": 0.0, "can_cross": False, "priority": None}
        with patch("random.random", return_value=0.5):
            results = self.v2v.broadcast_vehicle_info("V1", vehicle_data, 0.0)
        assert "V2" in results

    def test_receiver_gets_v2v_message(self):
        vehicle_data = {"vehicle_id": "V1", "position": (300, 500), "velocity": 20.0,
                        "direction": (1, 0), "vehicle_type": "regular",
                        "state": "approaching", "eta_to_intersection": 5.0,
                        "timestamp": 0.0, "can_cross": False, "priority": None}
        with patch("random.random", return_value=0.5):
            self.v2v.broadcast_vehicle_info("V1", vehicle_data, 0.0)
        messages = self.v2v.get_received_messages("V2", current_time=1.0)
        assert len(messages) >= 1

    def test_sender_does_not_receive_own_broadcast(self):
        vehicle_data = {"vehicle_id": "V1", "position": (300, 500), "velocity": 20.0,
                        "direction": (1, 0), "vehicle_type": "regular",
                        "state": "approaching", "eta_to_intersection": 5.0,
                        "timestamp": 0.0, "can_cross": False, "priority": None}
        with patch("random.random", return_value=0.5):
            self.v2v.broadcast_vehicle_info("V1", vehicle_data, 0.0)
        messages = self.v2v.get_received_messages("V1", current_time=1.0)
        assert all(m.sender_id != "V1" for m in messages)


class TestV2ICommunication:

    def setup_method(self):
        self.v2i = V2ICommunication(rsu_position=config.RSU_POSITION)
        self.v2i.register_vehicle("V1")
        self.v2i.register_vehicle("V2")

    def _vehicle_info(self, vid: str, pos=(100, 500)):
        return {"vehicle_id": vid, "position": pos, "velocity": 20.0,
                "direction": (1, 0), "vehicle_type": "regular",
                "state": "approaching", "eta_to_intersection": 5.0,
                "timestamp": 0.0, "can_cross": False, "priority": None}

    def test_vehicle_to_rsu_message_delivered(self):
        with patch("random.random", return_value=0.5):
            self.v2i.send_vehicle_info_to_rsu("V1", self._vehicle_info("V1"), 0.0)
        messages = self.v2i.get_rsu_messages(current_time=1.0)
        assert any(m.sender_id == "V1" for m in messages)

    def test_rsu_only_gets_rsu_addressed_mail(self):
        with patch("random.random", return_value=0.5):
            self.v2i.send_vehicle_info_to_rsu("V1", self._vehicle_info("V1"), 0.0)
            self.v2i.send_vehicle_info_to_rsu("V2", self._vehicle_info("V2"), 0.0)
        messages = self.v2i.get_rsu_messages(current_time=1.0)
        assert all(m.receiver_id == "RSU" for m in messages)

    def test_priority_decision_delivered_to_correct_vehicle(self):
        self.v2i.vehicle_registry["V1"]["last_info"] = self._vehicle_info("V1")
        with patch("random.random", return_value=0.5):
            self.v2i.send_priority_decision("V1", priority_level=1, current_time=0.0)
        msgs_v1 = self.v2i.get_vehicle_messages("V1", current_time=1.0)
        msgs_v2 = self.v2i.get_vehicle_messages("V2", current_time=1.0)
        assert any(m.payload.get("priority") == 1 for m in msgs_v1)
        assert len(msgs_v2) == 0, "V2 must not receive V1's priority assignment"
