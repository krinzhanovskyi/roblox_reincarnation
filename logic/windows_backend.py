import ctypes
from ctypes import wintypes as w
from pathlib import PureWindowsPath
import sys
import time


class AutomationError(RuntimeError):
    pass


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [("wVk", w.WORD), ("wScan", w.WORD), ("dwFlags", w.DWORD),
                ("time", w.DWORD), ("dwExtraInfo", ctypes.c_size_t)]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [("dx", w.LONG), ("dy", w.LONG), ("mouseData", w.DWORD),
                ("dwFlags", w.DWORD), ("time", w.DWORD),
                ("dwExtraInfo", ctypes.c_size_t)]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", w.DWORD), ("wParamL", w.WORD), ("wParamH", w.WORD)]


class INPUTUNION(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _anonymous_ = ("data",)
    _fields_ = [("type", w.DWORD), ("data", INPUTUNION)]


class WindowsBackend:
    PLAYER_NAMES = {"robloxplayerbeta.exe", "robloxplayer.exe"}

    def __init__(self):
        if sys.platform != "win32":
            raise AutomationError("Anti-AFK is supported on Windows only.")
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self.enum_callback = ctypes.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)
        signatures = {
            "GetForegroundWindow": ([], w.HWND),
            "IsWindow": ([w.HWND], w.BOOL),
            "IsWindowVisible": ([w.HWND], w.BOOL),
            "IsIconic": ([w.HWND], w.BOOL),
            "GetWindow": ([w.HWND, w.UINT], w.HWND),
            "EnumWindows": ([self.enum_callback, w.LPARAM], w.BOOL),
            "GetWindowThreadProcessId": ([w.HWND, ctypes.POINTER(w.DWORD)], w.DWORD),
            "SetForegroundWindow": ([w.HWND], w.BOOL),
            "ShowWindowAsync": ([w.HWND, ctypes.c_int], w.BOOL),
            "GetAsyncKeyState": ([ctypes.c_int], w.SHORT),
            "SendInput": ([w.UINT, ctypes.POINTER(INPUT), ctypes.c_int], w.UINT),
        }
        for name, (arguments, result) in signatures.items():
            function = getattr(self.user32, name)
            function.argtypes, function.restype = arguments, result
        self.kernel32.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
        self.kernel32.OpenProcess.restype = w.HANDLE
        self.kernel32.CloseHandle.argtypes = [w.HANDLE]
        self.kernel32.CloseHandle.restype = w.BOOL
        self.kernel32.QueryFullProcessImageNameW.argtypes = [
            w.HANDLE, w.DWORD, w.LPWSTR, ctypes.POINTER(w.DWORD)
        ]
        self.kernel32.QueryFullProcessImageNameW.restype = w.BOOL

    def foreground(self):
        return self.user32.GetForegroundWindow()

    def exists(self, hwnd):
        return bool(self.user32.IsWindow(hwnd))

    def minimized(self, hwnd):
        return bool(self.user32.IsIconic(hwnd))

    def minimize(self, hwnd):
        if self.exists(hwnd):
            self.user32.ShowWindowAsync(hwnd, 6)

    def _is_player(self, hwnd):
        pid = w.DWORD()
        self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        process = self.kernel32.OpenProcess(0x1000, False, pid.value)
        if not process:
            return False
        try:
            size = w.DWORD(32768)
            path = ctypes.create_unicode_buffer(size.value)
            if not self.kernel32.QueryFullProcessImageNameW(
                process, 0, path, ctypes.byref(size)
            ):
                return False
            return PureWindowsPath(path.value).name.lower() in self.PLAYER_NAMES
        finally:
            self.kernel32.CloseHandle(process)

    def find_roblox(self):
        windows = []

        @self.enum_callback
        def collect(hwnd, _parameter):
            if (self.user32.IsWindowVisible(hwnd)
                    and not self.user32.GetWindow(hwnd, 4)
                    and self._is_player(hwnd)):
                windows.append(hwnd)
            return True

        if not self.user32.EnumWindows(collect, 0):
            raise AutomationError("Could not enumerate application windows.")
        current = self.foreground()
        if current in windows:
            return current
        if len(windows) > 1:
            raise AutomationError("Multiple Roblox windows found. Keep one player open.")
        if not windows:
            raise AutomationError("Roblox Player was not found. Open a game first.")
        return windows[0]

    def _key(self, virtual_key, *, up=False, scan_code=0):
        event = INPUT()
        event.type = 1  # INPUT_KEYBOARD
        event.ki = KEYBDINPUT(
            0 if scan_code else virtual_key, scan_code,
            (0x0008 if scan_code else 0) | (0x0002 if up else 0), 0, 0,
        )
        if self.user32.SendInput(1, ctypes.byref(event), ctypes.sizeof(INPUT)) != 1:
            raise AutomationError("Windows blocked keyboard input. Check application privileges.")

    def _wait_foreground(self, hwnd):
        deadline = time.monotonic() + 0.5
        while time.monotonic() < deadline:
            if self.foreground() == hwnd:
                return True
            time.sleep(0.02)
        return self.foreground() == hwnd

    def activate(self, hwnd):
        if not self.exists(hwnd):
            raise AutomationError("The target window has been closed.")
        if self.minimized(hwnd):
            self.user32.ShowWindowAsync(hwnd, 9)  # SW_RESTORE
        self.user32.SetForegroundWindow(hwnd)
        if self._wait_foreground(hwnd):
            return
        if any(self.user32.GetAsyncKeyState(key) & 0x8000
               for key in (0x10, 0x11, 0x12, 0x5B, 0x5C)):
            raise AutomationError("Window switching was blocked while a modifier key was held.")
        try:
            self._key(0x12)
            self.user32.SetForegroundWindow(hwnd)
        finally:
            self._key(0x12, up=True)
        if not self._wait_foreground(hwnd):
            raise AutomationError("Windows did not allow switching to the target window.")

    def jump(self, hwnd, stop):
        if any(self.user32.GetAsyncKeyState(key) & 0x8000
               for key in (0x10, 0x11, 0x12, 0x20, 0x5B, 0x5C)):
            raise AutomationError("Jump skipped because Space or a modifier key is held.")
        if stop.is_set():
            return False
        if self.foreground() != hwnd or not self._is_player(hwnd):
            raise AutomationError("Roblox lost focus. No jump was sent.")
        try:
            self._key(0x20, scan_code=0x39)
            stop.wait(0.10)
        finally:
            self._key(0x20, up=True, scan_code=0x39)
        return True
