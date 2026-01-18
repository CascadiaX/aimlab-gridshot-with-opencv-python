# 🎯 Aim Lab Gridshot 自动化脚本 (OpenCV)

[![English](https://img.shields.io/badge/Docs-English-blue)](README.md)

一个基于计算机视觉的实验项目，用于自动化 **Aim Lab Gridshot** 模式中的目标捕获。本项目演示了如何使用 Python 和 OpenCV 实现实时目标检测、路径优化和精确鼠标控制。

![示例](example.png)

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.11+-5C3EE8?logo=opencv&logoColor=white)
![Windows](https://img.shields.io/badge/Windows-0078D6?logo=windows&logoColor=white)

## ✨ 功能特性

- **HSV 颜色检测** - 使用 HSV 色彩空间过滤检测青色目标球
- **TSP 路径优化** - 求解小规模旅行商问题，找到穿过所有可见目标的最短路径
- **幽灵过滤** - 防止在目标消失动画期间重复瞄准
- **窗口句柄捕获** - 使用 `dxcam` + `win32gui` 实现快速精准的屏幕捕获
- **开环控制** - 精确的光标移动与灵敏度校准

## 🧠 工作原理

### 目标检测
CV 流水线将每帧图像转换为 HSV 色彩空间，应用颜色掩码提取青色目标球。通过轮廓检测提取候选区域，并按面积和宽高比过滤以排除噪声。

### 路径规划 (TSP)
屏幕上最多同时显示 3 个目标，脚本通过暴力枚举求解小规模 **旅行商问题 (TSP)**（N≤4 时可行）。从当前光标位置出发，评估所有可能的访问顺序，选择总欧几里得距离最短的路径。这确保了目标访问顺序最优，实现最大速度。

### 鼠标控制
控制器使用原生 Win32 `mouse_event` 调用实现低延迟光标移动。路径插值将大幅移动分解为小步，以在高 DPI 设置下保持精度。

## 🏗️ 架构

```
main.py              主循环 (开环控制)
├── capture.py       窗口句柄捕获 (dxcam + win32gui)
├── vision.py        HSV 颜色检测流水线
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

- 按 `F4` 开启/关闭自动化
- 脚本在后台运行，正常玩 Gridshot 即可

## ⚙️ 配置说明

编辑 `config.py` 调整参数：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `ROI_WIDTH/HEIGHT` | 捕获区域大小 | 800×640 |
| `SENSITIVITY_MULT` | 鼠标灵敏度倍数 | 2.89 |
| `BALL_COLOR_LOWER/UPPER` | 目标的 HSV 颜色范围 | 青色 |
| `GHOST_TIME` | 忽略刚击中目标的时间 (ms) | 80 |

## 🛠️ 工具

| 工具 | 说明 |
|------|------|
| `tools/roi_calibrator.py` | 校准 ROI 偏移对齐 |
| `tools/auto_sensitivity_calibrator.py` | 自动校准鼠标灵敏度 |

## ⚠️ 免责声明

本项目仅供**学习研究**使用，旨在演示计算机视觉技术，不应用于在竞技场景中获取不公平优势。使用自动化工具可能违反 Aim Lab 的服务条款，请负责任地使用，风险自负。

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)
