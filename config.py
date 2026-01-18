# config.py
import numpy as np
import win32con

# --- Desktop Resolution ---
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2

# --- ROI Settings ---
ROI_WIDTH = 800
ROI_HEIGHT = 640

_base_left = CENTER_X - (ROI_WIDTH // 2)
_base_top = CENTER_Y - (ROI_HEIGHT // 2)

# CALIBRATED OFFSETS (from roi_calibrator.py)
# These values align ROI center with the game's crosshair
ROI_OFFSET_X = 30
ROI_OFFSET_Y = -60

ROI_LEFT = _base_left + ROI_OFFSET_X
ROI_TOP = _base_top + ROI_OFFSET_Y

def get_roi():
    return {"top": ROI_TOP, "left": ROI_LEFT, "width": ROI_WIDTH, "height": ROI_HEIGHT}

# --- Vision Settings ---
BALL_COLOR_LOWER = np.array([83, 92, 80])
BALL_COLOR_UPPER = np.array([133, 255, 255])
MIN_CONTOUR_AREA = 400
MIN_ASPECT_RATIO = 0.6
MAX_ASPECT_RATIO = 1.4

# --- Control Settings (V22 OPEN-LOOP SNAP) ---
# Kp - Not used in V24 pure open-loop (uses SENSITIVITY_MULT directly)
Kp = 1.0                   
Kp_STEP = 0.05
MAX_DELTA = 999             
OFFSET_FIX = [0, 0]         

# SENSITIVITY MULTIPLIER (Critical for DPI/Game Scaling)
# If mouse is moving LESS than expected, INCREASE this value
# Common values: 1.0 (100% DPI), 1.25 (125% DPI), 1.5 (150% DPI), 2.0 (200% DPI)
# Or tune based on in-game sensitivity
SENSITIVITY_MULT = 2.89     # Auto-calibrated

# FRICTION BOOST
MIN_MOVE_DIST = 2           

# V22 PHYSICS WAIT (Critical for Blind Shot)
# This is the wait AFTER move, BEFORE shot
# Increased base for higher accuracy
PHYSICS_BASE = 0.015        # 15ms (was 10ms)
PHYSICS_FACTOR = 0.00004    # 4ms per 100px
PHYSICS_CAP = 0.030         # 30ms max

# Shoot Threshold (If already close, skip move, just shoot)
INSTANT_SHOOT_DIST = 15     # If within 15px, just click directly

# Dynamic Shoot Radius (for closed-loop mode)
SHOOT_RADIUS_FACTOR = 0.45  # 45% of ball radius

SHOOT_COOLDOWN = 0.05       # 50ms
POST_SHOT_DELAY = 0.01      # 10ms (quick for closed-loop)

# POST-SHOT BLIND PERIOD (Critical for Open-Loop)
# This is the time we wait AFTER shooting before capturing again
# Purpose: Let game world settle, kill animation play, new ball spawn
# Too short = re-target same ball = wasted shots
# Too long = slow
BLIND_PERIOD = 0.015        # 15ms - balanced

# --- Anti-Recoil (Minimal, since open-loop) ---
GHOST_DIST = 60             
GHOST_TIME = 0.08           # 80ms

# --- Hotkeys ---
HOTKEY_TOGGLE   = win32con.VK_F4
HOTKEY_UP       = win32con.VK_UP
HOTKEY_DOWN     = win32con.VK_DOWN
