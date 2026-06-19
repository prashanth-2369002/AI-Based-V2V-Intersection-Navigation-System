"""
Unit tests for BMS SOC estimation logic (pure Python mirror of the C++ lookup table).
These tests validate the interpolation algorithm without requiring hardware.
"""
import pytest

# ── Mirror the SOC lookup table from bms.cpp ──────────────────────────────────

SOC_TABLE_VOLT = [3.00, 3.20, 3.40, 3.60, 3.70, 3.80, 3.90, 4.00, 4.10, 4.20]
SOC_TABLE_PCT  = [0,    5,    10,   30,   50,   70,   85,   93,   98,   100]


def estimate_soc(cell_voltage: float) -> float:
    """Python mirror of bms.cpp estimateSOC()."""
    if cell_voltage <= SOC_TABLE_VOLT[0]:
        return float(SOC_TABLE_PCT[0])
    if cell_voltage >= SOC_TABLE_VOLT[-1]:
        return float(SOC_TABLE_PCT[-1])
    for i in range(1, len(SOC_TABLE_VOLT)):
        if cell_voltage <= SOC_TABLE_VOLT[i]:
            ratio = ((cell_voltage - SOC_TABLE_VOLT[i - 1]) /
                     (SOC_TABLE_VOLT[i] - SOC_TABLE_VOLT[i - 1]))
            return SOC_TABLE_PCT[i - 1] + ratio * (SOC_TABLE_PCT[i] - SOC_TABLE_PCT[i - 1])
    return 100.0


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestSOCBoundaries:
    def test_empty_battery(self):
        assert estimate_soc(3.00) == 0.0

    def test_below_empty_clamps_to_zero(self):
        assert estimate_soc(2.50) == 0.0

    def test_full_battery(self):
        assert estimate_soc(4.20) == 100.0

    def test_above_full_clamps_to_100(self):
        assert estimate_soc(4.30) == 100.0


class TestSOCInterpolation:
    def test_midpoint_3v2_to_3v4(self):
        # Midpoint between 3.20V (5%) and 3.40V (10%) should be 7.5%
        result = estimate_soc(3.30)
        assert abs(result - 7.5) < 0.01

    def test_midpoint_3v6_to_3v7(self):
        # Midpoint between 3.60V (30%) and 3.70V (50%) should be 40%
        result = estimate_soc(3.65)
        assert abs(result - 40.0) < 0.01

    def test_exact_table_values(self):
        for volt, pct in zip(SOC_TABLE_VOLT, SOC_TABLE_PCT):
            assert abs(estimate_soc(volt) - pct) < 0.01, f"Failed at {volt}V → expected {pct}%"

    def test_soc_monotonically_increasing(self):
        voltages = [v / 100 for v in range(300, 421)]
        soc_values = [estimate_soc(v) for v in voltages]
        for i in range(1, len(soc_values)):
            assert soc_values[i] >= soc_values[i - 1], (
                f"SOC not monotonic at {voltages[i]}V: {soc_values[i]} < {soc_values[i-1]}"
            )

    def test_soc_always_in_range(self):
        for volt_int in range(250, 440):
            soc = estimate_soc(volt_int / 100)
            assert 0.0 <= soc <= 100.0, f"SOC out of range [{soc}] at {volt_int/100}V"


class TestFaultThresholds:
    """Validate the protection threshold logic (mirrored from config.h)."""

    CELL_COUNT        = 3
    VOLT_CUTOFF       = 4.25
    TEMP_CUTOFF_C     = 45.0
    CURRENT_MAX_A     = 4.5

    def is_overvoltage(self, pack_voltage: float) -> bool:
        return (pack_voltage / self.CELL_COUNT) > self.VOLT_CUTOFF

    def is_overtemp(self, temp_c: float) -> bool:
        return temp_c > self.TEMP_CUTOFF_C

    def is_overcurrent(self, current_a: float) -> bool:
        return current_a > self.CURRENT_MAX_A

    def test_overvoltage_trip(self):
        assert self.is_overvoltage(12.80) is True   # 4.267V/cell > 4.25

    def test_no_overvoltage_below_limit(self):
        assert self.is_overvoltage(12.60) is False  # 4.20V/cell OK

    def test_overtemp_trip(self):
        assert self.is_overtemp(46.0) is True

    def test_no_overtemp_at_limit(self):
        assert self.is_overtemp(45.0) is False      # Exactly at limit → no trip

    def test_overcurrent_trip(self):
        assert self.is_overcurrent(5.0) is True

    def test_overcurrent_safe(self):
        assert self.is_overcurrent(4.5) is False
