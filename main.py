# main.py
import cv2
import numpy as np
import time
import math
import os
import sys
import winsound
import dxcam 
import itertools

import config
from vision import Vision
from controller import Controller
from capture import WindowCapture

def solve_tsp_best_next(start_x, start_y, targets):
    """Returns the target that starts the optimal path."""
    n = len(targets)
    if n == 0: return None
    if n == 1: return targets[0]
    
    if n > 4:
        targets.sort(key=lambda t: t[4]) 
        subset = targets[:4]
    else:
        subset = targets

    min_total_dist = float('inf')
    best_first_target = None
    
    for perm in itertools.permutations(subset):
        current_dist = 0
        curr_x, curr_y = start_x, start_y
        for t in perm:
            tx, ty = t[2], t[3]
            dist = math.sqrt((tx - curr_x)**2 + (ty - curr_y)**2)
            current_dist += dist
            curr_x, curr_y = tx, ty
            
        if current_dist < min_total_dist:
            min_total_dist = current_dist
            best_first_target = perm[0]
            
    return best_first_target

def main():
    print("=== Aim Lab Assistant: V24 (REFINED OPEN-LOOP) ===")
    print(">>> MODE: MOVE ONCE -> SHOOT ONCE -> NEXT TARGET <<<")
    
    # Use WindowCapture for handle-based capture
    camera = WindowCapture(window_title="aimlab_tb", region_size=(config.ROI_WIDTH, config.ROI_HEIGHT))
    
    vision = Vision()
    controller = Controller()
    
    cx_roi = config.ROI_WIDTH // 2
    cy_roi = config.ROI_HEIGHT // 2
    
    active = False
    last_shot_time = 0
    
    # Stats
    frame_count = 0
    shot_count_session = 0
    hit_count = 0
    last_log_time = time.time()
    info = "Ready"

    print(">>> READY. Press F4. <<<")

    f4_was_down = False

    while True:
        # Input Check
        f4_down = controller.is_key_down(config.HOTKEY_TOGGLE)
        if f4_down and not f4_was_down:
            active = not active
            if active:
                print("\n>>> [ON] REFINED OPEN-LOOP ACTIVE <<<")
                winsound.Beep(1000, 50)
                shot_count_session = 0
            else:
                print("\n>>> [OFF] <<<")
                winsound.Beep(500, 50)
        f4_was_down = f4_down
        
        if not active:
            time.sleep(0.01)
            continue

        # === OPEN-LOOP CYCLE ===
        
        # 1. CAPTURE
        result = camera.grab()
        if result is None or result[0] is None: 
            continue
        frame, _, _ = result
        
        # 2. VISION
        targets, _ = vision.find_targets(frame)
        
        if not targets:
            continue
            
        # 3. PARSE & FILTER (Ghost Busting)
        parsed_targets = []
        curr_t = time.time()
        time_since_shot = curr_t - last_shot_time
        
        for (tx, ty, area) in targets:
            dx = tx - cx_roi
            dy = ty - cy_roi
            sq_dist = dx*dx + dy*dy
            
            # Ghost Filter
            if time_since_shot < config.GHOST_TIME and math.sqrt(sq_dist) < config.GHOST_DIST:
                continue
                
            parsed_targets.append((dx, dy, tx, ty, sq_dist, area))
            
        if not parsed_targets:
            continue

        # 4. TARGET SELECTION (TSP for optimal path)
        if len(parsed_targets) >= 2:
            target = solve_tsp_best_next(cx_roi, cy_roi, parsed_targets)
        else:
            target = parsed_targets[0]
        
        if not target:
            continue
            
        dx, dy, tx, ty, sq_dist, area = target
        dist = math.sqrt(sq_dist)
        
        # 5. COOLDOWN CHECK
        curr_t = time.time()
        if curr_t - last_shot_time < config.SHOOT_COOLDOWN:
            continue
        
        # 6. ACTION: MOVE -> WAIT -> SHOOT (One shot per target)
        
        if dist < config.INSTANT_SHOOT_DIST:
            # Already on target, just shoot
            controller.click()
            last_shot_time = time.time()
            shot_count_session += 1
            info = f"INSTANT! ({int(dist)}px)"
        else:
                # Calculate move with sensitivity calibration
            move_x = int(dx * config.SENSITIVITY_MULT)
            move_y = int(dy * config.SENSITIVITY_MULT)
            
            # PATH INTERPOLATION - break large moves into steps
            STEP_SIZE = 150  # max pixels per step
            total_move = math.sqrt(move_x**2 + move_y**2)
            
            if total_move > STEP_SIZE:
                # Calculate number of steps needed
                num_steps = int(math.ceil(total_move / STEP_SIZE))
                step_x = move_x / num_steps
                step_y = move_y / num_steps
                
                # Execute interpolated moves
                for i in range(num_steps):
                    controller.move_mouse(int(step_x), int(step_y))
                    time.sleep(0.003)  # 3ms between steps
            else:
                # Small move, execute directly
                controller.move_mouse(move_x, move_y)
            
            # PHYSICS WAIT - enough time for game to process move
            # Use fixed 25ms for consistency
            time.sleep(0.015)
            
            # SHOOT (blind - trust the math)
            controller.click()
            last_shot_time = time.time()
            shot_count_session += 1
            
            info = f"d:{int(dist)}px m:({move_x},{move_y})"
        
        # POST-SHOT WAIT - let game register hit, ball disappear
        time.sleep(config.BLIND_PERIOD)

        # Stats
        frame_count += 1
        curr_time = time.time()
        if curr_time - last_log_time >= 2.0: 
            fps = frame_count / (curr_time - last_log_time)
            print(f"{info} | FPS: {int(fps)} | Shots: {shot_count_session}                    ", end='\r')
            frame_count = 0
            last_log_time = curr_time

if __name__ == "__main__":
    main()
