"""Keyboard control module - handles all keyboard operations."""

import pyautogui
import pyperclip


def type_text(text, interval=0):
    """Type string character by character."""
    pyautogui.typewrite(text, interval=interval) if text.isascii() else _type_unicode(text, interval)
    return {"success": True}


def _type_unicode(text, interval=0):
    """Handle unicode text by using clipboard paste."""
    import time
    for char in text:
        if char.isascii():
            pyautogui.typewrite(char, interval=0)
        else:
            pyperclip.copy(char)
            pyautogui.hotkey("ctrl", "v")
        if interval > 0:
            time.sleep(interval)


def press_key(key):
    """Press and release a single key."""
    pyautogui.press(key)
    return {"success": True}


def hotkey(*keys):
    """Press key combination (e.g., ctrl+c)."""
    pyautogui.hotkey(*keys)
    return {"success": True}


def key_down(key):
    """Hold key down."""
    pyautogui.keyDown(key)
    return {"success": True}


def key_up(key):
    """Release key."""
    pyautogui.keyUp(key)
    return {"success": True}


def write_instant(text):
    """Paste text via clipboard (faster for long text)."""
    old_clipboard = pyperclip.paste()
    pyperclip.copy(text)
    pyautogui.hotkey("ctrl", "v")
    # Restore old clipboard after a brief delay
    import time
    time.sleep(0.05)
    pyperclip.copy(old_clipboard)
    return {"success": True}
