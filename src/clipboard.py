"""Clipboard module - handles clipboard get/set operations."""

import win32clipboard
import win32con
import io
from PIL import Image


def get_text():
    """Get current clipboard text content."""
    try:
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_UNICODETEXT):
            data = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
            return {"success": True, "text": data}
        return {"success": True, "text": ""}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        try:
            win32clipboard.CloseClipboard()
        except:
            pass


def set_text(text):
    """Set clipboard text content."""
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32con.CF_UNICODETEXT)
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        try:
            win32clipboard.CloseClipboard()
        except:
            pass


def clear():
    """Clear clipboard."""
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        try:
            win32clipboard.CloseClipboard()
        except:
            pass


def get_image():
    """Get clipboard image as base64 PNG (if available)."""
    import base64
    try:
        win32clipboard.OpenClipboard()
        if win32clipboard.IsClipboardFormatAvailable(win32con.CF_DIB):
            data = win32clipboard.GetClipboardData(win32con.CF_DIB)
            # Parse DIB header to get dimensions
            # This is a simplified approach - use PIL for robust parsing
            buffer = io.BytesIO()
            # Create BMP from DIB by adding BMP header
            bmp_header = b'BM' + (len(data) + 14).to_bytes(4, 'little') + b'\x00\x00\x00\x00\x36\x00\x00\x00'
            buffer.write(bmp_header)
            buffer.write(data)
            buffer.seek(0)
            image = Image.open(buffer)
            
            # Convert to PNG base64
            png_buffer = io.BytesIO()
            image.save(png_buffer, format="PNG")
            png_buffer.seek(0)
            b64 = base64.b64encode(png_buffer.getvalue()).decode("utf-8")
            return {"success": True, "image": b64, "format": "png"}
        return {"success": False, "error": "No image in clipboard"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        try:
            win32clipboard.CloseClipboard()
        except:
            pass
