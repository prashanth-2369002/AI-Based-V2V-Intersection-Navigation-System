"""
Standalone payment calculation utility.
Used by the Flask app and importable in tests independently of Flask context.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


DEFAULT_RATE_RS_PER_KWH = 8.0   # ₹ per kWh


@dataclass
class SessionSummary:
    uid: str
    start_time: datetime
    end_time: datetime
    energy_wh: float
    unit_rate: float

    @property
    def duration(self) -> timedelta:
        return self.end_time - self.start_time

    @property
    def energy_kwh(self) -> float:
        return self.energy_wh / 1000.0

    @property
    def cost_rs(self) -> float:
        return round(self.energy_kwh * self.unit_rate, 2)

    @property
    def duration_str(self) -> str:
        total = int(self.duration.total_seconds())
        h, rem = divmod(total, 3600)
        m, s   = divmod(rem, 60)
        return f"{h:02d}:{m:02d}:{s:02d}"

    def receipt(self) -> str:
        lines = [
            "=" * 36,
            "     SMART EV CHARGING RECEIPT",
            "=" * 36,
            f"  UID       : {self.uid}",
            f"  Start     : {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"  End       : {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"  Duration  : {self.duration_str}",
            f"  Energy    : {self.energy_wh:.2f} Wh  ({self.energy_kwh:.4f} kWh)",
            f"  Rate      : Rs {self.unit_rate:.2f} / kWh",
            "-" * 36,
            f"  TOTAL     : Rs {self.cost_rs:.2f}",
            "=" * 36,
        ]
        return "\n".join(lines)


def calculate_cost(energy_wh: float, rate: float = DEFAULT_RATE_RS_PER_KWH) -> float:
    """Return cost in Rupees for a given energy amount and unit rate."""
    if energy_wh < 0:
        raise ValueError(f"energy_wh must be non-negative, got {energy_wh}")
    if rate < 0:
        raise ValueError(f"rate must be non-negative, got {rate}")
    return round((energy_wh / 1000.0) * rate, 2)


def estimate_duration_minutes(energy_wh: float, power_w: float) -> float:
    """Estimate how many minutes it will take to charge given energy at a constant power."""
    if power_w <= 0:
        raise ValueError("power_w must be positive")
    return (energy_wh / power_w) * 60.0
