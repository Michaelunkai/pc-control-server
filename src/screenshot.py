"""Screenshot module - handles screen capture operations."""

import base64
import io

import pyautogui
from PIL import Image


def capture_full():
    """Capture entire screen, return PIL Image."""
    return pyautogui.screenshot()


def capture_region(x, y, width, height):
    """Capture specific region of screen."""
    return pyautogui.screenshot(region=(x, y, width, height))


def capture_to_base64(image=None, format="JPEG", quality=85):
    """Capture screen and return as base64 string."""
    if image is None:
        image = capture_full()
    
    buffer = io.BytesIO()
    if format.upper() == "JPEG":
        # Convert RGBA to RGB for JPEG
        if image.mode == "RGBA":
            image = image.convert("RGB")
        image.save(buffer, format="JPEG", quality=quality)
    else:
        image.save(buffer, format=format)
    
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def capture_to_file(filepath, format="PNG"):
    """Save screenshot to file."""
    image = capture_full()
    image.save(filepath, format=format)
    return {"success": True, "path": filepath}


def get_pixel_color(x, y):
    """Get RGB color at coordinate."""
    image = pyautogui.screenshot(region=(x, y, 1, 1))
    pixel = image.getpixel((0, 0))
    return {"r": pixel[0], "g": pixel[1], "b": pixel[2]}


def locate_on_screen(image_path, confidence=0.9):
    """Find image on screen, return coordinates."""
    try:
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        if location:
            center = pyautogui.center(location)
            return {
                "found": True,
                "x": center[0],
                "y": center[1],
                "left": location.left,
                "top": location.top,
                "width": location.width,
                "height": location.height,
            }
        return {"found": False}
    except Exception as e:
        return {"found": False, "error": str(e)}
