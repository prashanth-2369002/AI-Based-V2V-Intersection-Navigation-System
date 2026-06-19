# Contributing to Smart EV Charging System

Thank you for your interest in contributing! This is a diploma-level academic project, and we welcome improvements, bug reports, and documentation enhancements.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Reporting Issues](#reporting-issues)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Commit Message Format](#commit-message-format)
- [Branch Naming](#branch-naming)

---

## Code of Conduct

Be respectful, constructive, and inclusive. This is an educational project — questions and beginner contributions are welcome.

---

## How to Contribute

### Types of Contributions We Accept

- **Bug fixes** — incorrect calculations, broken dashboard routes, firmware crashes
- **Documentation improvements** — clearer explanations, corrected pin maps, better diagrams
- **Test additions** — more unit tests for BMS logic or payment calculator
- **Simulation support** — Wokwi JSON configurations or Proteus project files
- **New features** — only if discussed in an issue first

### What We Do Not Accept

- Changes that introduce fabricated benchmark results
- Hardware claims not verifiable on the specified components
- Dependencies that require paid APIs or cloud services without a free tier

---

## Reporting Issues

Before opening an issue:
1. Check existing [issues](../../issues) to avoid duplicates
2. For firmware bugs, include your ESP32 board variant and Arduino core version
3. For dashboard bugs, include Python version, OS, and the error traceback

**Issue template:**

```
**Describe the bug:**
A clear description of what is wrong.

**Steps to reproduce:**
1. ...
2. ...

**Expected behavior:**
What should happen.

**Environment:**
- OS:
- Python version:
- Arduino IDE version:
- ESP32 core version:
```

---

## Submitting Changes

1. **Fork** the repository
2. **Create a branch** from `main` (see [Branch Naming](#branch-naming))
3. **Make your changes** — one logical change per PR
4. **Run tests** before submitting

```bash
cd tests
pytest -v
```

5. **Commit** with a clear message (see [Commit Message Format](#commit-message-format))
6. **Open a Pull Request** against `main`

PRs should:
- Reference the related issue (`Closes #12`)
- Include a short description of *what* changed and *why*
- Not break existing tests

---

## Coding Standards

### Firmware (C++ / Arduino)

- Use `camelCase` for variables and functions
- Use `UPPER_SNAKE_CASE` for constants and `#define` macros
- Keep functions under 40 lines; extract helpers if longer
- No `delay()` in the main loop — use non-blocking timing with `millis()`
- Document any magic numbers with an inline comment explaining the source

```cpp
// Good
#define TEMP_CUTOFF_C   45.0    // IEC 62133 cell limit for Li-ion
float calculateSOC(float voltage, float capacity);

// Bad
delay(1000);
float x = voltage * 0.8;
```

### Python (Dashboard)

- Follow [PEP 8](https://pep8.org/)
- Use type hints for all function signatures
- Flask routes must not contain business logic — delegate to model/service layer
- All database writes must go through SQLAlchemy models, not raw SQL

```python
# Good
def calculate_cost(energy_kwh: float, rate: float) -> float:
    return round(energy_kwh * rate, 2)

# Bad
cost = e * r
```

### Documentation

- Use plain English; avoid jargon without explanation
- All Mermaid diagrams must render correctly on GitHub
- Update the relevant `docs/` file if your change affects system behavior

---

## Commit Message Format

Follow the [Conventional Commits](https://www.conventionalcommits.org/) standard:

```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

**Types:**

| Type | When to use |
|---|---|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `test` | Adding or fixing tests |
| `refactor` | Code restructure, no behavior change |
| `chore` | Build, CI, tooling changes |

**Examples:**

```
feat(bms): add passive cell balancing detection

fix(dashboard): correct SOC percentage overflow above 100%

docs(readme): add Wokwi simulation instructions

test(payment): add edge case for zero-duration session
```

---

## Branch Naming

```
feat/short-description
fix/short-description
docs/short-description
test/short-description
```

Examples:
```
feat/multi-port-support
fix/relay-cutoff-timing
docs/update-pin-mapping
```

---

Thank you for helping make this project better.
