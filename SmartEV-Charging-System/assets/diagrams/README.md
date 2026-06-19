# Diagrams

This folder holds exported diagram images and the demo GIF referenced in the README.

## Files Expected Here

| Filename | Description | Source |
|---|---|---|
| `block_diagram.png` | High-level block diagram of the system | Export from draw.io or hand-draw and scan |
| `circuit_schematic.png` | Circuit schematic PNG export | Export from Fritzing or EasyEDA |
| `demo.gif` | Screen-recorded demo GIF (~15–30 seconds) | Record with OBS or ShareX, convert with ffmpeg |
| `state_machine.png` | Battery state machine diagram | Export Mermaid diagram from docs/architecture.md |
| `wiring_diagram.png` | Colour-coded wiring guide | Fritzing breadboard view export |

---

## How to Create the Demo GIF

A good demo GIF shows the full flow in under 30 seconds:

1. Dashboard open at `http://localhost:5000` (idle state)
2. Run `python simulation/mqtt_simulator.py` in a terminal
3. Watch the SOC bar, power chart, and temperature update in real time
4. Session ends, history table updates with cost

### Recording Tools (Free)

| Tool | Platform | Notes |
|---|---|---|
| OBS Studio | Win/Mac/Linux | Record screen → export MP4 |
| ShareX | Windows | Direct GIF recording with region select |
| Kap | macOS | Lightweight GIF recorder |
| Peek | Linux | Simple animated GIF recorder |

### Converting MP4 → GIF with ffmpeg

```bash
ffmpeg -i demo_recording.mp4 \
       -vf "fps=10,scale=800:-1:flags=lanczos" \
       -loop 0 \
       demo.gif
```

- `fps=10` — 10 frames per second keeps file size under 5 MB
- `scale=800:-1` — 800px wide, auto height
- `-loop 0` — loop forever

---

## How to Export Mermaid Diagrams

The architecture Mermaid diagrams in `docs/architecture.md` can be exported as PNG:

1. Copy the Mermaid code block
2. Paste at [mermaid.live](https://mermaid.live)
3. Click **Download PNG** (top right)
4. Save to this folder with the appropriate filename
