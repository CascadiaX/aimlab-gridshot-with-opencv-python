# vision.py
import cv2
import numpy as np
import config

class Vision:
    def __init__(self):
        self.kernel = np.ones((3,3), np.uint8)

    def find_targets(self, frame):
        """
        Returns list of tuples: (cx, cy, area)
        """
        if frame is None:
            return [], None

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, config.BALL_COLOR_LOWER, config.BALL_COLOR_UPPER)
        
        # Gridshot is clean, but a small dilate can help solidify the ball shape
        # for better centroid calculation.
        # mask = cv2.dilate(mask, self.kernel, iterations=1)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        valid_targets = []
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < config.MIN_CONTOUR_AREA:
                continue
            
            x, y, w, h = cv2.boundingRect(cnt)
            if h <= 0: continue
            
            ratio = w / h
            if ratio < config.MIN_ASPECT_RATIO or ratio > config.MAX_ASPECT_RATIO:
                continue
            
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                # Return Area for debug
                valid_targets.append((cx, cy, area))
                
        return valid_targets, mask
