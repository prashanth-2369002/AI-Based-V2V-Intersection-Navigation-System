"""
Hardware Interface Module — Raspberry Pi 5
Abstracts GPIO, HC-SR04 ultrasonic sensor, L298N motor driver,
and SSD1306 OLED display behind clean Python interfaces.

On non-RPi platforms (Windows / macOS / Linux without GPIO) the module
runs in STUB mode: all hardware calls are no-ops that print to console,
so the full simulation stack can be tested without physical hardware.
"""

import time
import argparse
import threading
from typing import Optional

# ---------------------------------------------------------------------------
# GPIO / hardware availability detection
# ---------------------------------------------------------------------------

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    _GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    _GPIO_AVAILABLE = False

try:
    from luma.core.interface.serial import i2c
    from luma.oled.device import ssd1306
    from luma.core.render import canvas
    _OLED_AVAILABLE = True
except ImportError:
    _OLED_AVAILABLE = False


# ---------------------------------------------------------------------------
# HC-SR04 Ultrasonic Sensor
# ---------------------------------------------------------------------------

class UltrasonicSensor:
    """
    HC-SR04 distance sensor driver.

    Pinout (Raspberry Pi BCM numbering):
        TRIG → GPIO 23
        ECHO → GPIO 24  (connect via 1kΩ / 2kΩ voltage divider to 3.3 V)
    """

    TRIG_PIN = 23
    ECHO_PIN = 24
    SOUND_SPEED_CM_S = 34300  # cm/s at ~20 °C

    def __init__(self, trig_pin: int = TRIG_PIN, echo_pin: int = ECHO_PIN):
        self.trig_pin = trig_pin
        self.echo_pin = echo_pin
        self.gpio_available = _GPIO_AVAILABLE

        if self.gpio_available:
            GPIO.setup(self.trig_pin, GPIO.OUT)
            GPIO.setup(self.echo_pin, GPIO.IN)
            GPIO.output(self.trig_pin, False)
            time.sleep(0.05)  # sensor settling time

    def measure_distance(self) -> float:
        """
        Trigger a pulse and return the measured distance in centimetres.
        Returns -1.0 on timeout or if GPIO is unavailable (stub mode).
        """
        if not self.gpio_available:
            import random
            stub_distance = 45.0 + random.uniform(-5, 5)
            print(f"[STUB] UltrasonicSensor: distance = {stub_distance:.1f} cm")
            return stub_distance

        # Send 10 µs trigger pulse
        GPIO.output(self.trig_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trig_pin, False)

        # Wait for echo start (timeout 0.1 s)
        start = time.time()
        pulse_start = start
        while GPIO.input(self.echo_pin) == 0:
            pulse_start = time.time()
            if time.time() - start > 0.1:
                return -1.0

        # Wait for echo end
        pulse_end = pulse_start
        while GPIO.input(self.echo_pin) == 1:
            pulse_end = time.time()
            if time.time() - pulse_start > 0.1:
                return -1.0

        duration = pulse_end - pulse_start
        distance = (duration * self.SOUND_SPEED_CM_S) / 2
        return round(distance, 2)

    def is_obstacle_detected(self, threshold_cm: float = 20.0) -> bool:
        """Return True if an obstacle is closer than threshold_cm."""
        dist = self.measure_distance()
        return 0 < dist < threshold_cm

    def cleanup(self) -> None:
        """Release GPIO pins."""
        if self.gpio_available:
            GPIO.cleanup([self.trig_pin, self.echo_pin])


# ---------------------------------------------------------------------------
# L298N Motor Controller
# ---------------------------------------------------------------------------

class MotorController:
    """
    L298N dual H-bridge motor driver.

    Pinout (BCM):
        IN1 → GPIO 17    IN2 → GPIO 27   (left motor direction)
        IN3 → GPIO 22    IN4 → GPIO 10   (right motor direction)
        ENA → GPIO 18    ENB → GPIO 13   (PWM speed control)
    """

    IN1, IN2 = 17, 27
    IN3, IN4 = 22, 10
    ENA, ENB = 18, 13
    PWM_FREQ = 100  # Hz

    def __init__(self):
        self.gpio_available = _GPIO_AVAILABLE
        self._left_pwm: Optional[object] = None
        self._right_pwm: Optional[object] = None

        if self.gpio_available:
            for pin in (self.IN1, self.IN2, self.IN3, self.IN4, self.ENA, self.ENB):
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, False)

            self._left_pwm = GPIO.PWM(self.ENA, self.PWM_FREQ)
            self._right_pwm = GPIO.PWM(self.ENB, self.PWM_FREQ)
            self._left_pwm.start(0)
            self._right_pwm.start(0)

    def _set_direction(self, in1: bool, in2: bool, in3: bool, in4: bool) -> None:
        if self.gpio_available:
            GPIO.output(self.IN1, in1)
            GPIO.output(self.IN2, in2)
            GPIO.output(self.IN3, in3)
            GPIO.output(self.IN4, in4)

    def set_speed(self, left_speed: float, right_speed: float) -> None:
        """Set independent PWM duty cycle (0–100) for left and right motors."""
        left_speed = max(0, min(100, left_speed))
        right_speed = max(0, min(100, right_speed))
        if self.gpio_available:
            self._left_pwm.ChangeDutyCycle(left_speed)
            self._right_pwm.ChangeDutyCycle(right_speed)
        else:
            print(f"[STUB] MotorController.set_speed: L={left_speed:.0f}% R={right_speed:.0f}%")

    def forward(self, speed: float = 70) -> None:
        """Drive both motors forward."""
        self._set_direction(True, False, True, False)
        self.set_speed(speed, speed)
        if not self.gpio_available:
            print(f"[STUB] MotorController.forward(speed={speed})")

    def backward(self, speed: float = 70) -> None:
        """Drive both motors backward."""
        self._set_direction(False, True, False, True)
        self.set_speed(speed, speed)
        if not self.gpio_available:
            print(f"[STUB] MotorController.backward(speed={speed})")

    def turn_left(self, speed: float = 60) -> None:
        """Pivot left: right motor forward, left motor backward."""
        self._set_direction(False, True, True, False)
        self.set_speed(speed, speed)
        if not self.gpio_available:
            print(f"[STUB] MotorController.turn_left(speed={speed})")

    def turn_right(self, speed: float = 60) -> None:
        """Pivot right: left motor forward, right motor backward."""
        self._set_direction(True, False, False, True)
        self.set_speed(speed, speed)
        if not self.gpio_available:
            print(f"[STUB] MotorController.turn_right(speed={speed})")

    def stop(self) -> None:
        """Cut motor power (coast stop)."""
        self._set_direction(False, False, False, False)
        self.set_speed(0, 0)
        if not self.gpio_available:
            print("[STUB] MotorController.stop()")

    def cleanup(self) -> None:
        """Stop PWM and release GPIO pins."""
        self.stop()
        if self.gpio_available:
            if self._left_pwm:
                self._left_pwm.stop()
            if self._right_pwm:
                self._right_pwm.stop()
            GPIO.cleanup([self.IN1, self.IN2, self.IN3, self.IN4, self.ENA, self.ENB])


# ---------------------------------------------------------------------------
# SSD1306 OLED Display
# ---------------------------------------------------------------------------

class OLEDDisplay:
    """
    0.96″ I²C OLED SSD1306 display driver (128×64 pixels).

    Requires: luma.oled  (`pip install luma.oled`)
    I²C address: 0x3C (default)
    """

    WIDTH, HEIGHT = 128, 64

    def __init__(self, i2c_port: int = 1, i2c_address: int = 0x3C):
        self.i2c_address = i2c_address
        self.display_available = _OLED_AVAILABLE
        self._device = None

        if self.display_available:
            try:
                serial = i2c(port=i2c_port, address=i2c_address)
                self._device = ssd1306(serial, width=self.WIDTH, height=self.HEIGHT)
            except Exception as exc:
                print(f"[OLED] Init failed: {exc} — running in stub mode")
                self.display_available = False

    def show_text(self, lines: list) -> None:
        """
        Render up to 4 lines of text on the OLED.

        Args:
            lines: List of strings (max 4).
        """
        if not self.display_available:
            print("[STUB] OLED:", " | ".join(str(ln) for ln in lines))
            return

        with canvas(self._device) as draw:
            for idx, line in enumerate(lines[:4]):
                draw.text((0, idx * 16), str(line), fill="white")

    def show_status(self, distance_cm: float, state: str, priority: int) -> None:
        """Convenience method: show distance, state, and priority."""
        lines = [
            "V2V Nav System",
            f"Dist: {distance_cm:.1f} cm",
            f"State: {state}",
            f"Priority: {'GO' if priority == 1 else 'WAIT'}",
        ]
        self.show_text(lines)

    def clear(self) -> None:
        """Blank the display."""
        if self.display_available and self._device:
            self._device.clear()
        else:
            print("[STUB] OLED: clear()")

    def cleanup(self) -> None:
        """Clear display and release I²C."""
        self.clear()


# ---------------------------------------------------------------------------
# Composite Hardware Interface
# ---------------------------------------------------------------------------

class HardwareInterface:
    """
    Composite interface that ties together the sensor, motor, and display.

    In live mode, runs a control loop that:
    1. Reads distance from HC-SR04.
    2. Sends telemetry over V2I (placeholder: prints to console).
    3. Receives priority assignment (placeholder).
    4. Drives motors based on priority + obstacle distance.
    5. Updates OLED with current status.
    """

    OBSTACLE_THRESHOLD_CM = 20.0
    CROSSING_SPEED = 60
    APPROACH_SPEED = 40
    HOLD_SPEED = 10

    def __init__(self, vehicle_id: str = "V1"):
        self.vehicle_id = vehicle_id
        self.sensor = UltrasonicSensor()
        self.motor = MotorController()
        self.display = OLEDDisplay()
        self.running = False
        self._priority = 0
        self._state = "IDLE"
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Initialise hardware and show splash screen."""
        self._state = "APPROACHING"
        self.display.show_text([
            "V2V System",
            f"ID: {self.vehicle_id}",
            "Initialising...",
            "",
        ])
        time.sleep(1)
        print(f"[HW] {self.vehicle_id} hardware interface started.")

    def stop(self) -> None:
        """Stop motors and blank display."""
        self.running = False
        self.motor.stop()
        self.display.clear()

    def run_live_mode(self, duration_seconds: float = 60.0) -> None:
        """
        Run the hardware control loop for `duration_seconds`.

        This simulates the OBU logic that would run on each Raspberry Pi
        in a real deployment. Priority assignment is printed/mocked here;
        in a real system it arrives over the V2I channel.
        """
        self.running = True
        self.start()

        end_time = time.time() + duration_seconds
        step = 0

        try:
            while self.running and time.time() < end_time:
                distance = self.sensor.measure_distance()

                # Simulate receiving priority from RSU every ~5 steps
                if step % 5 == 0:
                    # In a real system: read from V2I socket
                    self._priority = 1 if (step // 5) % 2 == 0 else 0

                self.execute_movement(self._priority, distance)
                self.update_display(distance, self._state, self._priority)

                time.sleep(0.1)
                step += 1

        except KeyboardInterrupt:
            print("\n[HW] Interrupted by user.")
        finally:
            self.cleanup()

    def execute_movement(self, priority: int, distance_cm: float) -> None:
        """
        Decide motor action based on priority and obstacle distance.

        Args:
            priority:    1 = clear to cross, 0 = hold
            distance_cm: Current obstacle distance from ultrasonic sensor
        """
        with self._lock:
            if distance_cm > 0 and distance_cm < self.OBSTACLE_THRESHOLD_CM:
                self.motor.stop()
                self._state = "OBSTACLE_HOLD"
                print(f"[HW] {self.vehicle_id}: OBSTACLE at {distance_cm:.1f} cm — STOP")

            elif priority == 1:
                self._state = "CROSSING"
                self.motor.forward(self.CROSSING_SPEED)

            else:
                self._state = "WAITING"
                self.motor.set_speed(self.HOLD_SPEED, self.HOLD_SPEED)

    def update_display(self, distance: float, state: str, priority: int) -> None:
        """Push current status to OLED."""
        self.display.show_status(distance, state, priority)

    def cleanup(self) -> None:
        """Release all hardware resources."""
        self.motor.cleanup()
        self.sensor.cleanup()
        self.display.cleanup()
        if _GPIO_AVAILABLE:
            GPIO.cleanup()
        print(f"[HW] {self.vehicle_id} cleanup complete.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="V2V Hardware Interface — Raspberry Pi 5"
    )
    parser.add_argument(
        "--vehicle-id", default="V1",
        help="Vehicle identifier (default: V1)"
    )
    parser.add_argument(
        "--mode", choices=["live", "stub"], default="stub",
        help="'live' requires physical RPi GPIO; 'stub' prints to console"
    )
    parser.add_argument(
        "--duration", type=float, default=30.0,
        help="How many seconds to run the control loop (default: 30)"
    )
    args = parser.parse_args()

    print("=" * 60)
    print("V2V HARDWARE INTERFACE")
    print("=" * 60)
    print(f"Vehicle: {args.vehicle_id}")
    print(f"Mode:    {args.mode}")
    print(f"GPIO:    {'available' if _GPIO_AVAILABLE else 'not available (stub mode)'}")
    print(f"OLED:    {'available' if _OLED_AVAILABLE else 'not available (stub mode)'}")
    print()

    hw = HardwareInterface(vehicle_id=args.vehicle_id)
    hw.run_live_mode(duration_seconds=args.duration)


if __name__ == "__main__":
    main()
