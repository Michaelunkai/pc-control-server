"""Window manager module - handles window listing, focusing, and management."""

import ctypes
import ctypes.wintypes
import time

import win32gui
import win32con
import win32process


def list_windows():
    """Return list of all visible windows with details."""
    windows = []

    def enum_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:  # Skip windows with no title
                rect = win32gui.GetWindowRect(hwnd)
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                placement = win32gui.GetWindowPlacement(hwnd)
                is_minimized = placement[1] == win32con.SW_SHOWMINIMIZED
                is_maximized = placement[1] == win32con.SW_SHOWMAXIMIZED
                windows.append({
                    "hwnd": hwnd,
                    "title": title,
                    "pid": pid,
                    "rect": {
                        "left": rect[0],
                        "top": rect[1],
                        "right": rect[2],
                        "bottom": rect[3],
                        "width": rect[2] - rect[0],
                        "height": rect[3] - rect[1],
                    },
                    "minimized": is_minimized,
                    "maximized": is_maximized,
                })

    win32gui.EnumWindows(enum_callback, None)
    return windows


def get_active_window():
    """Return currently focused window info."""
    hwnd = win32gui.GetForegroundWindow()
    if hwnd:
        title = win32gui.GetWindowText(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        return {
            "hwnd": hwnd,
            "title": title,
            "rect": {
                "left": rect[0],
                "top": rect[1],
                "right": rect[2],
                "bottom": rect[3],
            },
        }
    return None


def focus_window(hwnd=None, title=None):
    """Bring window to front by handle or title substring."""
    if title and not hwnd:
        hwnd = _find_hwnd_by_title(title)
    if not hwnd:
        return {"success": False, "error": "Window not found"}

    try:
        # Try multiple methods to ensure focus
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        # Use Alt key trick to allow SetForegroundWindow
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        win32gui.SetForegroundWindow(hwnd)
        return {"success": True, "hwnd": hwnd}
    except Exception as e:
        # Fallback: use AttachThreadInput trick
        try:
            _force_focus(hwnd)
            return {"success": True, "hwnd": hwnd}
        except Exception as e2:
            return {"success": False, "error": str(e2)}


def _force_focus(hwnd):
    """Force focus using AttachThreadInput trick."""
    fore_thread = ctypes.windll.user32.GetWindowThreadProcessId(
        ctypes.windll.user32.GetForegroundWindow(), None
    )
    target_thread = ctypes.windll.user32.GetWindowThreadProcessId(hwnd, None)
    
    if fore_thread != target_thread:
        ctypes.windll.user32.AttachThreadInput(fore_thread, target_thread, True)
        ctypes.windll.user32.SetForegroundWindow(hwnd)
        ctypes.windll.user32.AttachThreadInput(fore_thread, target_thread, False)
    else:
        ctypes.windll.user32.SetForegroundWindow(hwnd)


def minimize_window(hwnd=None, title=None):
    """Minimize window."""
    if title and not hwnd:
        hwnd = _find_hwnd_by_title(title)
    if not hwnd:
        return {"success": False, "error": "Window not found"}
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    return {"success": True}


def maximize_window(hwnd=None, title=None):
    """Maximize window."""
    if title and not hwnd:
        hwnd = _find_hwnd_by_title(title)
    if not hwnd:
        return {"success": False, "error": "Window not found"}
    win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
    return {"success": True}


def restore_window(hwnd=None, title=None):
    """Restore window from minimized/maximized."""
    if title and not hwnd:
        hwnd = _find_hwnd_by_title(title)
    if not hwnd:
        return {"success": False, "error": "Window not found"}
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    return {"success": True}


def close_window(hwnd=None, title=None):
    """Close window."""
    if title and not hwnd:
        hwnd = _find_hwnd_by_title(title)
    if not hwnd:
        return {"success": False, "error": "Window not found"}
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    return {"success": True}


def move_window(hwnd, x, y):
    """Move window to position (keeps current size)."""
    rect = win32gui.GetWindowRect(hwnd)
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
    win32gui.MoveWindow(hwnd, x, y, width, height, True)
    return {"success": True}


def resize_window(hwnd, width, height):
    """Resize window (keeps current position)."""
    rect = win32gui.GetWindowRect(hwnd)
    win32gui.MoveWindow(hwnd, rect[0], rect[1], width, height, True)
    return {"success": True}


def set_window_rect(hwnd, x, y, width, height):
    """Move and resize window in one call."""
    win32gui.MoveWindow(hwnd, x, y, width, height, True)
    return {"success": True}


def find_window_by_title(title_substring):
    """Find first window containing text in title."""
    hwnd = _find_hwnd_by_title(title_substring)
    if hwnd:
        title = win32gui.GetWindowText(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        return {
            "found": True,
            "hwnd": hwnd,
            "title": title,
            "rect": {
                "left": rect[0],
                "top": rect[1],
                "right": rect[2],
                "bottom": rect[3],
            },
        }
    return {"found": False}


def wait_for_window(title_substring, timeout=10):
    """Wait until window appears, return its info."""
    start = time.time()
    while time.time() - start < timeout:
        hwnd = _find_hwnd_by_title(title_substring)
        if hwnd:
            title = win32gui.GetWindowText(hwnd)
            return {"success": True, "hwnd": hwnd, "title": title}
        time.sleep(0.2)
    return {"success": False, "error": f"Window '{title_substring}' not found within {timeout}s"}


def _find_hwnd_by_title(title_substring):
    """Internal: find window handle by title substring (case-insensitive)."""
    result = [None]
    title_lower = title_substring.lower()

    def enum_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title_lower in title.lower():
                result[0] = hwnd
                return False  # Stop enumeration
        return True

    try:
        win32gui.EnumWindows(enum_callback, None)
    except:
        pass  # EnumWindows raises when callback returns False
    return result[0]
