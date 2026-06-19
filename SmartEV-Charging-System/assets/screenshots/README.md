# Screenshots

Place your actual screenshot images in this folder. The filenames below match the references in the main `README.md`.

## Required Screenshots

| Filename | Description | How to capture |
|---|---|---|
| `dashboard_home.png` | Dashboard homepage showing SOC gauge, live voltage, current, and temperature cards | Open `http://localhost:5000` in browser, take a full-page screenshot |
| `session_active.png` | Active charging session with the real-time power graph updating | Start a session (or run the MQTT simulator), screenshot after ~30 seconds of data |
| `payment_history.png` | Payment and session history table with at least 3–4 completed sessions | Complete a few simulated sessions, then screenshot the history table |
| `lcd_display.jpg` | Photo of the physical LCD display during an active charging session showing SOC, voltage, and timer | Photograph the hardware with good lighting |
| `hardware_setup.jpg` | Bird's-eye photo of the full breadboard prototype | Photograph from above with all components visible and labelled |

## Screenshot Tips

- Use **1280 × 720** or **1920 × 1080** resolution for dashboard screenshots
- Crop to the relevant area — avoid capturing browser chrome / OS taskbar
- For dark-mode dashboard screenshots, no extra setup needed (dashboard is already dark-themed)
- Name files exactly as listed above — the README.md `![alt](assets/screenshots/filename.png)` references these exact paths

## Placeholder

Until real screenshots are taken, the README will show broken image icons. This is normal for a work-in-progress repository. Recruiters understand that hardware project screenshots require physical setup.
