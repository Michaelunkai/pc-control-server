"""Mouse control module - handles all mouse operations."""

import pyautogui


def move_to(x, y, duration=0):
    """Move mouse to absolute coordinates."""
    pyautogui.moveTo(x, y, duration=duration)
    return {"success": True, "x": x, "y": y}


def move_relative(dx, dy, duration=0):
    """Move mouse relative to current position."""
    pyautogui.moveRel(dx, dy, duration=duration)
    pos = pyautogui.position()
    return {"success": True, "x": pos[0], "y": pos[1]}


def click(x=None, y=None, button="left", clicks=1):
    """Click at position. If x,y not provided, clicks at current position."""
    pyautogui.click(x=x, y=y, button=button, clicks=clicks)
    return {"success": True}


def double_click(x=None, y=None):
    """Double click at position."""
    pyautogui.doubleClick(x=x, y=y)
    return {"success": True}


def right_click(x=None, y=None):
    """Right click at position."""
    pyautogui.rightClick(x=x, y=y)
    return {"success": True}


def middle_click(x=None, y=None):
    """Middle click at position."""
    pyautogui.middleClick(x=x, y=y)
    return {"success": True}


def drag_to(x, y, duration=0.2, button="left"):
    """Drag from current position to target."""
    pyautogui.dragTo(x, y, duration=duration, button=button)
    return {"success": True}


def drag_relative(dx, dy, duration=0.2, button="left"):
    """Drag relative to current position."""
    pyautogui.dragRel(dx, dy, duration=duration, button=button)
    return {"success": True}


def scroll(clicks, x=None, y=None):
    """Scroll wheel. Positive = up, negative = down."""
    pyautogui.scroll(clicks, x=x, y=y)
    return {"success": True}


def get_position():
    """Return current mouse position."""
    pos = pyautogui.position()
    return {"x": pos[0], "y": pos[1]}


def get_screen_size():
    """Return screen dimensions."""
    size = pyautogui.size()
    return {"width": size[0], "height": size[1]}
