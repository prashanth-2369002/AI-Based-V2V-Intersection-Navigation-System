"""
Unit tests for payment / billing calculation logic.
"""
import pytest
from datetime import datetime, timedelta

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'software'))
from payment.payment_handler import calculate_cost, estimate_duration_minutes, SessionSummary


class TestCalculateCost:
    def test_zero_energy_is_zero_cost(self):
        assert calculate_cost(0.0) == 0.0

    def test_one_kwh_at_default_rate(self):
        # Default rate is ₹8 / kWh; 1000 Wh = 1 kWh → ₹8.00
        assert calculate_cost(1000.0) == 8.0

    def test_half_kwh(self):
        assert calculate_cost(500.0) == 4.0

    def test_small_charge(self):
        # 100 Wh = 0.1 kWh → ₹0.80
        assert calculate_cost(100.0) == 0.80

    def test_custom_rate(self):
        assert calculate_cost(2000.0, rate=10.0) == 20.0

    def test_result_rounded_to_two_decimal_places(self):
        # 333 Wh at ₹8/kWh = ₹2.664 → rounds to ₹2.66
        cost = calculate_cost(333.0)
        assert cost == round(cost, 2)

    def test_negative_energy_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            calculate_cost(-10.0)

    def test_negative_rate_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            calculate_cost(100.0, rate=-5.0)


class TestEstimateDuration:
    def test_typical_charge(self):
        # 400 Wh at 100W → 4 hours = 240 minutes
        assert estimate_duration_minutes(400.0, 100.0) == pytest.approx(240.0)

    def test_zero_power_raises(self):
        with pytest.raises(ValueError, match="positive"):
            estimate_duration_minutes(100.0, 0.0)

    def test_negative_power_raises(self):
        with pytest.raises(ValueError, match="positive"):
            estimate_duration_minutes(100.0, -10.0)


class TestSessionSummary:
    def _make_session(self, energy_wh=500.0, duration_minutes=30, rate=8.0):
        start = datetime(2025, 6, 1, 10, 0, 0)
        end   = start + timedelta(minutes=duration_minutes)
        return SessionSummary(
            uid="A1B2C3D4",
            start_time=start,
            end_time=end,
            energy_wh=energy_wh,
            unit_rate=rate,
        )

    def test_cost_calculation(self):
        s = self._make_session(energy_wh=1000.0, rate=8.0)
        assert s.cost_rs == 8.0

    def test_duration_str_format(self):
        s = self._make_session(duration_minutes=90)
        assert s.duration_str == "01:30:00"

    def test_energy_kwh_conversion(self):
        s = self._make_session(energy_wh=2500.0)
        assert s.energy_kwh == pytest.approx(2.5)

    def test_receipt_contains_uid(self):
        s = self._make_session()
        assert "A1B2C3D4" in s.receipt()

    def test_receipt_contains_cost(self):
        s = self._make_session(energy_wh=1000.0, rate=8.0)
        assert "8.00" in s.receipt()

    def test_zero_energy_session(self):
        s = self._make_session(energy_wh=0.0)
        assert s.cost_rs == 0.0
