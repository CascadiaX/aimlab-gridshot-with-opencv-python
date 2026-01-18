# 🎯 Aim Lab Gridshot 自动瞄准机器人

[![English](https://img.shields.io/badge/Docs-English-blue)](README.md)

基于 Python 和 OpenCV 的 **Aim Lab Gridshot** 模式自动瞄准机器人。通过计算机视觉目标检测和路径优化算法实现高分。

![示例](example.png)

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.11+-5C3EE8?logo=opencv&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-0078D6?logo=windows&logoColor=white)

## ✨ 功能特性

- **HSV 颜色检测** - 使用 HSV 色彩空间过滤检测蓝色目标球
- **TSP 路径优化** - 使用旅行商算法找到最优目标顺序
- **幽灵过滤** - 防止重复瞄准刚击中的目标
- **窗口句柄捕获** - 使用 `dxcam` + `win32gui` 实现快速精准的屏幕捕获
- **开环控制** - 精确的鼠标移动和灵敏度校准

## 🏗️ 架构

```
main.py              主循环 (V24 开环架构)
├── capture.py       窗口句柄捕获 (dxcam + win32gui)
├── vision.py        HSV 颜色检测
├── tracker.py       多目标追踪器 (可选)
├── controller.py    鼠标控制 (ctypes 原始输入)
└── config.py        配置参数
```

## 🚀 快速开始

### 环境要求

- Windows 10/11
- Python 3.13+
- [UV](https://docs.astral.sh/uv/)（推荐）或 pip
- Aim Lab (Steam)

### 安装

```bash
# 克隆仓库
git clone https://github.com/CascadiaX/aimlab-gridshot-with-opencv-python.git
cd aimlab-gridshot-with-opencv-python

# 使用 UV 安装依赖
uv sync

# 或使用 pip
pip install -e .
```

### 校准

首次使用前，校准 ROI 偏移：

```bash
uv run tools/roi_calibrator.py
```

1. 打开 Aim Lab 并进入 Gridshot 模式
2. 使用 `I/K/J/L` 键调整偏移，直到绿色十字准星与游戏准星对齐
3. 按 `P` 打印数值，然后更新 `config.py`

### 运行

```bash
uv run main.py
```

- 按 `F4` 开启/关闭机器人
- 机器人在后台运行 - 正常玩 Gridshot 即可！

## ⚙️ 配置说明

编辑 `config.py` 调整参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `ROI_WIDTH/HEIGHT` | 捕获区域大小 | 800×640 |
| `SENSITIVITY_MULT` | 鼠标灵敏度倍数 | 2.89 |
| `BALL_COLOR_LOWER/UPPER` | 目标的 HSV 颜色范围 | 蓝色 |
| `GHOST_TIME` | 忽略刚击中目标的时间 (ms) | 80 |

## 🛠️ 工具

| 工具 | 说明 |
|------|------|
| `tools/roi_calibrator.py` | 校准 ROI 偏移对齐 |
| `tools/auto_sensitivity_calibrator.py` | 自动校准鼠标灵敏度 |

## ⚠️ 免责声明

本项目仅供**学习研究**使用。使用自动化工具可能违反 Aim Lab 的服务条款，风险自负。

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)
