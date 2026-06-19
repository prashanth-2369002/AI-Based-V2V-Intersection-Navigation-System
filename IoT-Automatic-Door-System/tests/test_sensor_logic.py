"""
Unit tests for sensor fusion decision logic.
Mirrors the C++ logic from firmware/main/main.ino in Python for fast CI testing.
"""

import pytest


# ─── Replicated decision logic ────────────────────────────────────────────────

AUTHORIZED_UIDS = {"A1B2C3D4", "11223344", "DEADBEEF"}
ULTRASONIC_TRIGGER_CM  = 100
ULTRASONIC_OBSTACLE_CM = 10
PROXIMITY_UNLOCK_CM    = 30


def should_open(pir: bool, distance_cm: int, rfid_uid: str | None) -> tuple[bool, str]:
    """
    Returns (open_door, reason).
    Mirrors the ESP32 main loop decision block.
    """
    if not pir:
        return False, "no_motion"
    if distance_cm < 0 or distance_cm > ULTRASONIC_TRIGGER_CM:
        return False, "out_of_range"

    if rfid_uid is not None:
        if rfid_uid in AUTHORIZED_UIDS:
            return True, "rfid"
        else:
            return False, "unauthorized_rfid"

    if distance_cm <= PROXIMITY_UNLOCK_CM:
        return True, "proximity"

    return False, "no_credential"


def is_obstacle(distance_cm: int) -> bool:
    return 0 < distance_cm < ULTRASONIC_OBSTACLE_CM


# ─── Tests ────────────────────────────────────────────────────────────────────

class TestMotionDetection:
    def test_no_pir_no_open(self):
        open_, reason = should_open(pir=False, distance_cm=50, rfid_uid="A1B2C3D4")
        assert not open_
        assert reason == "no_motion"

    def test_pir_only_out_of_range(self):
        open_, reason = should_open(pir=True, distance_cm=150, rfid_uid=None)
        assert not open_

    def test_pir_sensor_returns_error(self):
        open_, _ = should_open(pir=True, distance_cm=-1, rfid_uid=None)
        assert not open_


class TestRFIDAuthorization:
    def test_authorized_card_opens(self):
        open_, reason = should_open(pir=True, distance_cm=50, rfid_uid="A1B2C3D4")
        assert open_
        assert reason == "rfid"

    def test_all_authorized_cards(self):
        for uid in AUTHORIZED_UIDS:
            open_, _ = should_open(pir=True, distance_cm=50, rfid_uid=uid)
            assert open_, f"UID {uid} should be authorized"

    def test_unauthorized_card_denied(self):
        open_, reason = should_open(pir=True, distance_cm=50, rfid_uid="BADC0FFE")
        assert not open_
        assert reason == "unauthorized_rfid"

    def test_unknown_uid_denied(self):
        open_, _ = should_open(pir=True, distance_cm=50, rfid_uid="00000000")
        assert not open_

    def test_case_sensitivity(self):
        open_, _ = should_open(pir=True, distance_cm=50, rfid_uid="a1b2c3d4")
        assert not open_   # UIDs are case-sensitive (firmware stores uppercase)


class TestProximityUnlock:
    def test_close_proximity_opens(self):
        open_, reason = should_open(pir=True, distance_cm=25, rfid_uid=None)
        assert open_
        assert reason == "proximity"

    def test_boundary_30cm(self):
        open_, _ = should_open(pir=True, distance_cm=30, rfid_uid=None)
        assert open_

    def test_beyond_proximity_no_open(self):
        open_, _ = should_open(pir=True, distance_cm=31, rfid_uid=None)
        assert not open_


class TestObstacleDetection:
    def test_obstacle_at_5cm(self):
        assert is_obstacle(5) is True

    def test_no_obstacle_at_15cm(self):
        assert is_obstacle(15) is False

    def test_boundary_10cm(self):
        assert is_obstacle(10) is False  # exclusive boundary

    def test_sensor_error_not_obstacle(self):
        assert is_obstacle(-1) is False

    def test_zero_distance_not_obstacle(self):
        assert is_obstacle(0) is False


class TestEdgeCases:
    def test_rfid_takes_priority_over_proximity(self):
        # Authorized RFID + close proximity → rfid reason, not proximity
        open_, reason = should_open(pir=True, distance_cm=10, rfid_uid="A1B2C3D4")
        assert open_
        assert reason == "rfid"

    def test_denied_rfid_blocks_proximity_fallback(self):
        # Unauthorized card presented — door should NOT fall back to proximity
        open_, reason = should_open(pir=True, distance_cm=10, rfid_uid="BADC0FFE")
        assert not open_
        assert reason == "unauthorized_rfid"
