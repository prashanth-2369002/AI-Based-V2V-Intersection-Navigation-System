# Contributing

Contributions are welcome — bug fixes, new sensor modules, dashboard improvements, or documentation updates.

## Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/IoT-Automatic-Door-System.git
cd IoT-Automatic-Door-System

# Backend
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install flask paho-mqtt pytest pytest-cov flake8

# Run tests
cd ..
pytest tests/ -v
```

## Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/<name>` | `feature/face-recognition` |
| Bug fix | `fix/<name>` | `fix/ultrasonic-timeout` |
| Docs | `docs/<name>` | `docs/wiring-diagram` |
| Refactor | `refactor/<name>` | `refactor/state-machine` |

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add fingerprint sensor module
fix: correct ultrasonic voltage divider ratio
docs: update wiring diagram for relay module
test: add edge case for RFID UID case sensitivity
refactor: extract door state machine to separate file
```

## Pull Request Checklist

- [ ] Tests added or updated for the change
- [ ] `pytest tests/ -v` passes locally
- [ ] `flake8 backend/ tests/` produces no errors
- [ ] README updated if hardware or API changed
- [ ] Pin assignments updated in `docs/hardware-components.md` if wiring changed

## Firmware Contributions

- Test on physical hardware before submitting
- Note which ESP32 board and Arduino IDE / PlatformIO version was used
- Document new config parameters in `firmware/main/config.h`
- Keep `loop()` non-blocking — no `delay()` calls longer than 100 ms

## Code Style

**Python:** PEP 8, max line length 100, type hints for public functions.  
**C++ (Arduino):** 4-space indent, `camelCase` for variables, `UPPER_SNAKE` for constants.

## Reporting Issues

Include:
1. Hardware setup (which components, which ESP32 board)
2. Firmware version (commit hash)
3. Serial monitor output
4. Steps to reproduce
