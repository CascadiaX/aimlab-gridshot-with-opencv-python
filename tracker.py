# tracker.py
"""
Simple Nearest-Neighbor Multi-Target Tracker

Maintains stable IDs for targets across frames.
Replaces hardcoded ghost filter with tracking-based approach.
"""

import math
import time

class Track:
    """A single tracked target."""
    _id_counter = 0
    
    def __init__(self, x, y, area):
        Track._id_counter += 1
        self.id = Track._id_counter
        self.x = x
        self.y = y
        self.area = area
        self.last_seen = time.time()
        self.status = "active"  # "active", "shot", "dead"
        self.shot_time = 0
        
    def update(self, x, y, area):
        """Update track with new detection."""
        self.x = x
        self.y = y
        self.area = area
        self.last_seen = time.time()
        
    def mark_shot(self):
        """Mark this track as just shot."""
        self.status = "shot"
        self.shot_time = time.time()
        
    def is_ghost(self, ghost_timeout=0.1):
        """Check if this track is a ghost (recently shot)."""
        if self.status == "shot":
            if time.time() - self.shot_time < ghost_timeout:
                return True
            else:
                # Ghost timeout expired, ball still here = back to active
                self.status = "active"
        return False
    
    def distance_to(self, x, y):
        """Euclidean distance to a point."""
        return math.sqrt((self.x - x)**2 + (self.y - y)**2)


class SimpleTracker:
    """
    Nearest-neighbor tracker for multiple targets.
    
    Usage:
        tracker = SimpleTracker()
        
        # Each frame:
        detections = [(x1, y1, area1), (x2, y2, area2), ...]
        tracks = tracker.update(detections)
        
        # Get valid targets (not ghosts):
        valid = tracker.get_valid_targets()
        
        # After shooting at a track:
        tracker.mark_shot(track_id)
    """
    
    def __init__(self, max_match_dist=100, track_timeout=0.5, ghost_timeout=0.1):
        """
        Args:
            max_match_dist: Max distance to match detection to existing track
            track_timeout: Remove track if not seen for this long
            ghost_timeout: Ignore shot track for this long
        """
        self.tracks = {}  # id -> Track
        self.max_match_dist = max_match_dist
        self.track_timeout = track_timeout
        self.ghost_timeout = ghost_timeout
        
    def update(self, detections):
        """
        Update tracker with new detections.
        
        Args:
            detections: List of (x, y, area) tuples
            
        Returns:
            List of (track_id, x, y, area, is_ghost) tuples
        """
        current_time = time.time()
        
        # Remove stale tracks
        stale_ids = [
            tid for tid, track in self.tracks.items()
            if current_time - track.last_seen > self.track_timeout
        ]
        for tid in stale_ids:
            del self.tracks[tid]
        
        # Match detections to existing tracks (greedy nearest-neighbor)
        matched_track_ids = set()
        matched_det_indices = set()
        
        results = []
        
        # Sort by distance for greedy matching
        matches = []
        for det_idx, (dx, dy, area) in enumerate(detections):
            for tid, track in self.tracks.items():
                dist = track.distance_to(dx, dy)
                if dist < self.max_match_dist:
                    matches.append((dist, det_idx, tid, dx, dy, area))
        
        matches.sort(key=lambda m: m[0])  # Sort by distance
        
        for dist, det_idx, tid, dx, dy, area in matches:
            if det_idx in matched_det_indices or tid in matched_track_ids:
                continue
            
            # Match found
            track = self.tracks[tid]
            track.update(dx, dy, area)
            matched_track_ids.add(tid)
            matched_det_indices.add(det_idx)
            
            is_ghost = track.is_ghost(self.ghost_timeout)
            results.append((tid, dx, dy, area, is_ghost))
        
        # Create new tracks for unmatched detections
        for det_idx, (dx, dy, area) in enumerate(detections):
            if det_idx not in matched_det_indices:
                track = Track(dx, dy, area)
                self.tracks[track.id] = track
                results.append((track.id, dx, dy, area, False))
        
        # DELETE shot tracks that didn't match (ball truly disappeared)
        for tid in list(self.tracks.keys()):
            if tid not in matched_track_ids:
                track = self.tracks[tid]
                if track.status == "shot":
                    del self.tracks[tid]  # Ball is gone, remove track
        
        return results
    
    def get_valid_targets(self, results):
        """
        Filter results to only valid (non-ghost) targets.
        
        Args:
            results: Output from update()
            
        Returns:
            List of (track_id, x, y, area) for non-ghost targets
        """
        return [(tid, x, y, area) for tid, x, y, area, is_ghost in results if not is_ghost]
    
    def mark_shot(self, track_id):
        """Mark a track as just shot (will be ghost for ghost_timeout)."""
        if track_id in self.tracks:
            self.tracks[track_id].mark_shot()
            
    def reset(self):
        """Clear all tracks."""
        self.tracks.clear()
        Track._id_counter = 0

    def shift_tracks(self, dx, dy):
        """
        Compensate for camera movement.
        Shift all tracks by (dx, dy).
        
        If we moved mouse to aim at a target at (100, 0), the world moved left.
        Screen shift = (-100, 0).
        """
        for track in self.tracks.values():
            track.x += dx
            track.y += dy
