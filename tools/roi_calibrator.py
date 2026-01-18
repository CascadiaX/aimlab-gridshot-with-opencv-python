# tools/roi_calibrator.py
"""
ROI Calibration Tool

This tool helps you find the correct ROI_OFFSET_X and ROI_OFFSET_Y values.

How to use:
1. Run this script with Aim Lab open (in the mode you'll be playing)
2. A window will show the captured ROI with a GREEN CROSSHAIR at the center
3. The GREEN crosshair should align EXACTLY with the game's actual crosshair
4. Use GLOBAL HOTKEYS (work even when game has focus):
   - I/K: Adjust Y offset (up/down)
   - J/L: Adjust X offset (left/right)
5. Press 'P' to print/save the current offset values
6. Press 'Q' to quit
"""

import cv2
import dxcam
import numpy as np
import time
import ctypes

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

# Initial values (same as config.py)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
CENTER_X = SCREEN_WIDTH // 2
CENTER_Y = SCREEN_HEIGHT // 2

ROI_WIDTH = 800
ROI_HEIGHT = 640

# Start with no offset
offset_x = 0
offset_y = 0

def main():
    global offset_x, offset_y
    
    print("=== ROI CALIBRATION TOOL ===")
    print("GLOBAL HOTKEYS (work even when game has focus):")
    print("  I/K: Adjust Y offset (up/down)")
    print("  J/L: Adjust X offset (left/right)")
    print("  P: Print/Save offset values")
    print("  Q: Quit")
    print("")
    
    camera = dxcam.create(output_idx=0, output_color="BGR")
    
    cv2.namedWindow("ROI Calibrator", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("ROI Calibrator", 800, 640)
    
    # Debounce tracking
    last_key_time = {}
    debounce = 0.15  # 150ms between key repeats
    
    while True:
        # Calculate ROI position with current offset
        left = CENTER_X - (ROI_WIDTH // 2) + offset_x
        top = CENTER_Y - (ROI_HEIGHT // 2) + offset_y
        
        region = (left, top, left + ROI_WIDTH, top + ROI_HEIGHT)
        
        frame = camera.grab(region=region)
        if frame is None:
            time.sleep(0.01)
            continue
        
        # Draw crosshair at center (this should align with game crosshair)
        cx = ROI_WIDTH // 2
        cy = ROI_HEIGHT // 2
        
        # Draw thick green crosshair
        cv2.line(frame, (cx - 50, cy), (cx + 50, cy), (0, 255, 0), 2)
        cv2.line(frame, (cx, cy - 50), (cx, cy + 50), (0, 255, 0), 2)
        cv2.circle(frame, (cx, cy), 10, (0, 255, 0), 2)
        
        # Draw offset info
        info_text = f"Offset: X={offset_x}, Y={offset_y}"
        cv2.putText(frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(frame, "I/K=Y  J/L=X  P=Save  Q=Quit", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        cv2.imshow("ROI Calibrator", frame)
        cv2.waitKey(1)  # Still needed for OpenCV window to update
        
        curr_time = time.time()
        
        # Global key detection
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
                offset_y -= 5
                print(f"Offset: X={offset_x}, Y={offset_y}")
                
        if is_key_pressed(VK_K):  # DOWN
            if curr_time - last_key_time.get(VK_K, 0) > debounce:
                last_key_time[VK_K] = curr_time
                offset_y += 5
                print(f"Offset: X={offset_x}, Y={offset_y}")
                
        if is_key_pressed(VK_J):  # LEFT
            if curr_time - last_key_time.get(VK_J, 0) > debounce:
                last_key_time[VK_J] = curr_time
                offset_x -= 5
                print(f"Offset: X={offset_x}, Y={offset_y}")
                
        if is_key_pressed(VK_L):  # RIGHT
            if curr_time - last_key_time.get(VK_L, 0) > debounce:
                last_key_time[VK_L] = curr_time
                offset_x += 5
                print(f"Offset: X={offset_x}, Y={offset_y}")
    
    cv2.destroyAllWindows()
    print(f"\nFinal Offset: X={offset_x}, Y={offset_y}")

if __name__ == "__main__":
    main()
