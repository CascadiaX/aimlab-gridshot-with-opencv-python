# tools/auto_sensitivity_calibrator.py
"""
AUTO SENSITIVITY CALIBRATOR - Multi-Sample Version

Takes 10 measurements at different distances and calculates average ratio.
More accurate than single measurement.
"""

import cv2
import dxcam
import numpy as np
import math
import time
import ctypes
import winsound
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from vision import Vision

MOUSEEVENTF_MOVE = 0x0001
VK_F4 = 0x73
VK_Q = 0x51

user32 = ctypes.windll.user32

def is_key_pressed(vk_code):
    return user32.GetAsyncKeyState(vk_code) & 0x8000

def move_mouse(dx, dy):
    user32.mouse_event(MOUSEEVENTF_MOVE, int(dx), int(dy), 0, 0)

def main():
    print("=" * 60)
    print("AUTO SENSITIVITY CALIBRATOR - MULTI-SAMPLE")
    print("=" * 60)
    print("")
    print("This tool takes 10 measurements to find the precise SENSITIVITY_MULT")
    print("")
    print("Instructions:")
    print("1. Start Aim Lab Gridshot")
    print("2. Press F4 to run calibration (will measure 10 targets)")
    print("3. Wait for results")
    print("")
    print("Press Q to quit")
    print("")
    
    camera = dxcam.create(output_idx=0, output_color="BGR")
    monitor = config.get_roi()
    region = (monitor["left"], monitor["top"], 
              monitor["left"] + monitor["width"], 
              monitor["top"] + monitor["height"])
    
    vision = Vision()
    cx_roi = config.ROI_WIDTH // 2
    cy_roi = config.ROI_HEIGHT // 2
    
    f4_was_down = False
    
    while True:
        if is_key_pressed(VK_Q):
            print("Exiting...")
            break
            
        f4_down = is_key_pressed(VK_F4)
        
        if f4_down and not f4_was_down:
            print("\n>>> Starting multi-sample calibration...")
            winsound.Beep(1000, 50)
            
            ratios = []
            sample_count = 0
            max_samples = 10
            
            while sample_count < max_samples:
                time.sleep(0.2)  # Wait between samples
                
                # Capture
                frame1 = camera.grab(region=region)
                if frame1 is None:
                    continue
                    
                targets, _ = vision.find_targets(frame1)
                if not targets:
                    continue
                
                # Find target in good range (50-200px)
                best_target = None
                for (tx, ty, area) in targets:
                    dx = tx - cx_roi
                    dy = ty - cy_roi
                    dist = math.sqrt(dx*dx + dy*dy)
                    if 50 < dist < 200:
                        best_target = (tx, ty, dx, dy, dist)
                        break
                
                if not best_target:
                    continue
                
                tx, ty, dx, dy, dist1 = best_target
                
                # Move with MULT=1.0
                move_x = int(dx)
                move_y = int(dy)
                move_mouse(move_x, move_y)
                
                # Wait for game to process
                time.sleep(0.1)
                
                # Measure result
                frame2 = camera.grab(region=region)
                if frame2 is None:
                    continue
                    
                targets2, _ = vision.find_targets(frame2)
                if not targets2:
                    continue
                
                # Find nearest target to center
                min_dist2 = float('inf')
                for (tx2, ty2, area2) in targets2:
                    dx2 = tx2 - cx_roi
                    dy2 = ty2 - cy_roi
                    d2 = math.sqrt(dx2*dx2 + dy2*dy2)
                    if d2 < min_dist2:
                        min_dist2 = d2
                
                dist2 = min_dist2
                actual_move = dist1 - dist2
                
                if actual_move > 10:  # Valid measurement
                    ratio = dist1 / actual_move
                    ratios.append(ratio)
                    sample_count += 1
                    print(f"  Sample {sample_count}: dist={dist1:.0f}px, moved={actual_move:.0f}px, ratio={ratio:.3f}")
                    winsound.Beep(800, 30)
            
            if ratios:
                avg_ratio = np.mean(ratios)
                std_ratio = np.std(ratios)
                min_ratio = np.min(ratios)
                max_ratio = np.max(ratios)
                
                print(f"\n{'=' * 40}")
                print(f"CALIBRATION RESULTS ({len(ratios)} samples)")
                print(f"{'=' * 40}")
                print(f"  Average: {avg_ratio:.4f}")
                print(f"  Std Dev: {std_ratio:.4f}")
                print(f"  Min:     {min_ratio:.4f}")
                print(f"  Max:     {max_ratio:.4f}")
                print(f"")
                print(f">>> RECOMMENDED: SENSITIVITY_MULT = {avg_ratio:.3f}")
                print(f"")
                winsound.Beep(1500, 200)
            else:
                print("Failed to collect samples. Try again.")
            
        f4_was_down = f4_down
        time.sleep(0.01)

if __name__ == "__main__":
    main()
