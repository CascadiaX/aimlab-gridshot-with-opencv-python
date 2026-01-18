# roi_calibrator.py
"""
ROI Calibration Tool (Adapted for 640x480 Window Capture)

This tool helps you find the correct ROI_OFFSET_X and ROI_OFFSET_Y values.

How to use:
1. Run this script with Aim Lab open (windowed mode 640x480 recommended)
2. A window will show the captured ROI with a GREEN CROSSHAIR at the center
3. The GREEN crosshair should align EXACTLY with the game's actual crosshair
4. Use GLOBAL HOTKEYS:
   - I/K: Adjust Y offset (up/down)
   - J/L: Adjust X offset (left/right)
5. Press 'P' to print/save the current offset values
6. Press 'Q' to quit
"""

import cv2
import numpy as np
import time
import ctypes

# Fix DPI Awareness immediately
try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

import win32gui
import config
from capture import WindowCapture

# Win32 key codes
VK_I = 0x49
VK_K = 0x4B
VK_J = 0x4A
VK_L = 0x4C
VK_P = 0x50
VK_Q = 0x51

user32 = ctypes.windll.user32

def is_key_pressed(vk_code):
    return user32.GetAsyncKeyState(vk_code) & 0x8000

# Start with offsets from config
offset_x = config.ROI_OFFSET_X
offset_y = config.ROI_OFFSET_Y

def main():
    global offset_x, offset_y
    
    print("=== ROI CALIBRATION TOOL (Handler Capture) ===")
    print(f"Res: {config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}, ROI: {config.ROI_WIDTH}x{config.ROI_HEIGHT}")
    print("GLOBAL HOTKEYS:")
    print("  I/K: Adjust Y offset")
    print("  J/L: Adjust X offset")
    print("  P: Print/Save values")
    print("  Q: Quit")
    
    # Use WindowCapture (handle-based)
    camera = WindowCapture(window_title="aimlab_tb", region_size=(config.ROI_WIDTH, config.ROI_HEIGHT))
    
    if not camera.find_window():
        print("Waiting for 'aimlab_tb' window...")
    
    cv2.namedWindow("ROI Calibrator", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("ROI Calibrator", config.ROI_WIDTH, config.ROI_HEIGHT)
    
    # Debounce tracking
    last_key_time = {}
    debounce = 0.15
    
    while True:
        # Debug: Check client rect size
        if camera.hwnd:
             left, top, right, bottom = win32gui.GetClientRect(camera.hwnd)
             cw, ch = right-left, bottom-top
             # print(f"Client Size: {cw}x{ch}") # Optional debug spam
        
        # Apply current offsets to camera
        camera.user_offset_x = offset_x
        camera.user_offset_y = offset_y
        
        # Grab frame (uses handle + offsets)
        result = camera.grab()
        if result is None or result[0] is None:
            time.sleep(0.01)
            continue
        
        frame, _, _ = result
        
        # Draw green crosshair at visual center of the ROI
        cx = config.ROI_WIDTH // 2
        cy = config.ROI_HEIGHT // 2
        
        cv2.line(frame, (cx - 50, cy), (cx + 50, cy), (0, 255, 0), 2)
        cv2.line(frame, (cx, cy - 50), (cx, cy + 50), (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 10, (0, 255, 0), 2)
        
        # Draw offset info
        info_text = f"Offset: X={offset_x}, Y={offset_y}"
        cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(frame, "I/K=Y  J/L=X  P=Save  Q=Quit", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.imshow("ROI Calibrator", frame)
        cv2.waitKey(1)
        
        curr_time = time.time()
        
        # Key handling
        if is_key_pressed(VK_Q):
            break
            
        if is_key_pressed(VK_P):
            if curr_time - last_key_time.get(VK_P, 0) > debounce:
                last_key_time[VK_P] = curr_time
                print(f"\n=== SAVE THESE VALUES TO config.py ===")
                print(f"ROI_OFFSET_X = {offset_x}")
                print(f"ROI_OFFSET_Y = {offset_y}")
                print("=====================================\n")
                
        if is_key_pressed(VK_I):  # UP
            if curr_time - last_key_time.get(VK_I, 0) > debounce:
                last_key_time[VK_I] = curr_time
                offset_y -= 1  # Fine tune 1px
                print(f"Offset: X={offset_x}, Y={offset_y}")
                
        if is_key_pressed(VK_K):  # DOWN
            if curr_time - last_key_time.get(VK_K, 0) > debounce:
                last_key_time[VK_K] = curr_time
                offset_y += 1
                print(f"Offset: X={offset_x}, Y={offset_y}")
                
        if is_key_pressed(VK_J):  # LEFT
            if curr_time - last_key_time.get(VK_J, 0) > debounce:
                last_key_time[VK_J] = curr_time
                offset_x -= 1
                print(f"Offset: X={offset_x}, Y={offset_y}")
                
        if is_key_pressed(VK_L):  # RIGHT
            if curr_time - last_key_time.get(VK_L, 0) > debounce:
                last_key_time[VK_L] = curr_time
                offset_x += 1
                print(f"Offset: X={offset_x}, Y={offset_y}")
    
    cv2.destroyAllWindows()
    print(f"\nFinal Offset: X={offset_x}, Y={offset_y}")

if __name__ == "__main__":
    main()
