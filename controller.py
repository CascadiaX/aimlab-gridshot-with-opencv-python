# controller.py
import ctypes
import time
import win32con
import config

# Ctypes definitions for raw speed
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004

class Controller:
    def __init__(self):
        self.user32 = ctypes.windll.user32
        if not self.is_admin():
            print("WARNING: Not running as Admin. Input may fail.")

    def is_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def is_key_down(self, key_code):
        return self.user32.GetAsyncKeyState(key_code) & 0x8000

    def move_mouse(self, dx, dy):
        if dx == 0 and dy == 0: return
        self.user32.mouse_event(MOUSEEVENTF_MOVE, int(dx), int(dy), 0, 0)

    def click(self):
        self.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        import time
        time.sleep(0.015)  # 15ms hold
        self.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
