# 🎯 Aim Lab Gridshot Bot with OpenCV

[![中文文档](https://img.shields.io/badge/文档-中文版-blue)](README_CN.md)

An automated aim bot for **Aim Lab Gridshot** mode using Python and OpenCV. Achieves high scores through computer vision-based target detection and optimized path planning.

![Example](example.png)

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.11+-5C3EE8?logo=opencv&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-0078D6?logo=windows&logoColor=white)

## ✨ Features

- **HSV Color Detection** - Detects blue target balls using HSV color space filtering
- **TSP Path Optimization** - Uses traveling salesman algorithm to find optimal target order
- **Ghost Filtering** - Prevents re-targeting recently hit balls
- **Window Handle Capture** - Uses `dxcam` + `win32gui` for fast, accurate screen capture
- **Open-Loop Control** - Precise mouse movement with sensitivity calibration

## 🏗️ Architecture

```
main.py              Main loop (V24 Open-Loop)
├── capture.py       Window handle capture (dxcam + win32gui)
├── vision.py        HSV color detection
├── tracker.py       Multi-target tracker (optional)
├── controller.py    Mouse control (ctypes raw input)
└── config.py        Configuration parameters
```

## 🚀 Quick Start

### Prerequisites

- Windows 10/11
- Python 3.13+
- [UV](https://docs.astral.sh/uv/) (recommended) or pip
- Aim Lab (Steam)

### Installation

```bash
# Clone the repository
git clone https://github.com/CascadiaX/aimlab-gridshot-with-opencv-python.git
cd aimlab-gridshot-with-opencv-python

# Install dependencies with UV
uv sync

# Or with pip
pip install -e .
```

### Calibration

Before first use, calibrate your ROI offset:

```bash
uv run tools/roi_calibrator.py
```

1. Open Aim Lab and enter Gridshot mode
2. Adjust offsets with `I/K/J/L` keys until the green crosshair aligns with your game crosshair
3. Press `P` to print values, then update `config.py`

### Running

```bash
uv run main.py
```

- Press `F4` to toggle the bot ON/OFF
- The bot works in the background - just play Gridshot!

## ⚙️ Configuration

Edit `config.py` to tune parameters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ROI_WIDTH/HEIGHT` | Capture region size | 800×640 |
| `SENSITIVITY_MULT` | Mouse sensitivity multiplier | 2.89 |
| `BALL_COLOR_LOWER/UPPER` | HSV color range for targets | Blue |
| `GHOST_TIME` | Ignore recently shot targets (ms) | 80 |

## 🛠️ Tools

| Tool | Description |
|------|-------------|
| `tools/roi_calibrator.py` | Calibrate ROI offset alignment |
| `tools/auto_sensitivity_calibrator.py` | Auto-calibrate mouse sensitivity |

## ⚠️ Disclaimer

This project is for **educational purposes only**. Use of automation tools may violate Aim Lab's Terms of Service. Use at your own risk.

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.
