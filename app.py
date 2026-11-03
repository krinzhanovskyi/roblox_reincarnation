import ctypes

try:
    ctypes.windll.user32.SetProcessDpiAwarenessContext(
        ctypes.c_void_p(-4)
    )
except (AttributeError, OSError):
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except (AttributeError, OSError):
        pass

from ui.main_window import SettingsWindow


if __name__ == "__main__":
    SettingsWindow().mainloop()