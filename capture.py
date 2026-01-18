# capture.py
"""
Window Handle Capture using win32gui + dxcam
Uses window handle for coordinate lookup, dxcam for fast GPU capture
"""

import win32gui
import dxcam

class WindowCapture:
    """Capture frames from a specific window by handle using dxcam."""
    
    def __init__(self, window_title="aimlab_tb", region_size=(600, 500)):
        """
        Args:
            window_title: Window title to find (default: aimlab_tb)
            region_size: (width, height) of center region to capture
        """
        self.window_title = window_title
        self.region_width, self.region_height = region_size
        self.hwnd = None
        self.camera = dxcam.create(output_idx=0, output_color="BGR")
        # ROI offset in window client coordinates
        self.roi_offset_x = 0
        self.roi_offset_y = 0
        
    def find_window(self):
        """Find and cache the window handle."""
        self.hwnd = win32gui.FindWindow(None, self.window_title)
        if self.hwnd == 0:
            self.hwnd = None
            return False
        print(f"✓ Found window: {self.window_title} (hwnd={self.hwnd})")
        return True
        
    def grab(self):
        """
        Capture a frame from the center of the window.
        
        Returns:
            numpy array (BGR) or None if window not found
        """
        # Find window if not cached
        if self.hwnd is None:
            if not self.find_window():
                return None
        
        try:
            # Get window client area
            left, top, right, bottom = win32gui.GetClientRect(self.hwnd)
            client_width = right - left
            client_height = bottom - top
            
            # Calculate center region (ROI offset in window client coords)
            self.roi_offset_x = client_width // 2 - self.region_width // 2
            self.roi_offset_y = client_height // 2 - self.region_height // 2
            
            # Convert to screen coordinates
            screen_left, screen_top = win32gui.ClientToScreen(self.hwnd, (self.roi_offset_x, self.roi_offset_y))
            
            # Capture with dxcam (fast GPU capture)
            region = (
                screen_left, 
                screen_top, 
                screen_left + self.region_width, 
                screen_top + self.region_height
            )
            frame = self.camera.grab(region=region)
            return frame, screen_left, screen_top
            
        except Exception as e:
            # Window may have closed or moved
            self.hwnd = None
            return None, 0, 0
    
    def roi_to_window(self, roi_x, roi_y):
        """Convert ROI coordinates to window client coordinates."""
        return (self.roi_offset_x + roi_x, self.roi_offset_y + roi_y)
    
    def get_roi_size(self):
        """Return the region size as (width, height)."""
        return (self.region_width, self.region_height)
