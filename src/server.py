"""
PC Control Server - Local HTTP API for mouse, keyboard, screenshots, and window management.

Binds to 127.0.0.1 only (localhost). No external network access.
Designed to be compiled to EXE and run at Windows startup.
"""

import json
import logging
import os
import sys
import time
from functools import wraps
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify, request

# Add parent dir to path for imports
if getattr(sys, 'frozen', False):
    # Running as compiled EXE
    BASE_DIR = os.path.dirname(sys.executable)
    # PyInstaller extracts data files to sys._MEIPASS
    BUNDLE_DIR = getattr(sys, '_MEIPASS', BASE_DIR)
else:
    # Running as script
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    BUNDLE_DIR = BASE_DIR

# Add all possible module locations to path
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "src"))
sys.path.insert(0, BUNDLE_DIR)
sys.path.insert(0, os.path.join(BUNDLE_DIR, "src"))

import pyautogui
import config
import mouse_control
import keyboard_control
import screenshot
import window_manager
import clipboard

# ============================================================
# App Setup
# ============================================================

app = Flask(__name__)
START_TIME = time.time()

# Configure pyautogui
pyautogui.FAILSAFE = config.FAILSAFE
pyautogui.PAUSE = config.PAUSE

# ============================================================
# Logging Setup
# ============================================================

def setup_logging():
    """Configure logging to file and console."""
    log_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "server.log")

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # File handler (rotating, max 5MB, keep 3 backups)
    file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Reduce Flask's default logging noise
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    return logger


logger = setup_logging()

# ============================================================
# Auth Middleware (optional)
# ============================================================

def require_api_key(f):
    """Decorator to check API key if configured."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if config.API_KEY:
            key = request.headers.get("X-API-Key") or request.args.get("api_key")
            if key != config.API_KEY:
                return jsonify({"success": False, "error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

# ============================================================
# Error Handler
# ============================================================

@app.errorhandler(Exception)
def handle_error(e):
    """Return JSON error responses."""
    logger.error(f"Unhandled error: {e}", exc_info=True)
    return jsonify({"success": False, "error": str(e)}), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404


@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"success": False, "error": "Method not allowed"}), 405

# ============================================================
# Helper
# ============================================================

def get_json():
    """Get JSON body from request, handle empty body."""
    if request.is_json:
        return request.get_json()
    return {}

# ============================================================
# System Routes
# ============================================================

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ok",
        "uptime": round(time.time() - START_TIME, 1),
        "version": "1.0.0",
    })


@app.route("/api/screen/size", methods=["GET"])
@require_api_key
def screen_size():
    """Get screen dimensions."""
    size = pyautogui.size()
    return jsonify({"width": size[0], "height": size[1]})

# ============================================================
# Mouse Routes
# ============================================================

@app.route("/api/mouse/position", methods=["GET"])
@require_api_key
def mouse_position():
    """Get current mouse position."""
    result = mouse_control.get_position()
    return jsonify(result)


@app.route("/api/mouse/move", methods=["POST"])
@require_api_key
def mouse_move():
    """Move mouse to absolute coordinates."""
    data = get_json()
    x = data.get("x", 0)
    y = data.get("y", 0)
    duration = data.get("duration", 0)
    result = mouse_control.move_to(x, y, duration)
    logger.debug(f"Mouse move to ({x}, {y})")
    return jsonify(result)


@app.route("/api/mouse/move_relative", methods=["POST"])
@require_api_key
def mouse_move_relative():
    """Move mouse relative to current position."""
    data = get_json()
    dx = data.get("dx", 0)
    dy = data.get("dy", 0)
    duration = data.get("duration", 0)
    result = mouse_control.move_relative(dx, dy, duration)
    logger.debug(f"Mouse move relative ({dx}, {dy})")
    return jsonify(result)


@app.route("/api/mouse/click", methods=["POST"])
@require_api_key
def mouse_click():
    """Click at position."""
    data = get_json()
    x = data.get("x")
    y = data.get("y")
    button = data.get("button", "left")
    clicks = data.get("clicks", 1)
    result = mouse_control.click(x, y, button, clicks)
    logger.debug(f"Mouse click at ({x}, {y}) button={button} clicks={clicks}")
    return jsonify(result)


@app.route("/api/mouse/double_click", methods=["POST"])
@require_api_key
def mouse_double_click():
    """Double click at position."""
    data = get_json()
    x = data.get("x")
    y = data.get("y")
    result = mouse_control.double_click(x, y)
    logger.debug(f"Mouse double click at ({x}, {y})")
    return jsonify(result)


@app.route("/api/mouse/right_click", methods=["POST"])
@require_api_key
def mouse_right_click():
    """Right click at position."""
    data = get_json()
    x = data.get("x")
    y = data.get("y")
    result = mouse_control.right_click(x, y)
    logger.debug(f"Mouse right click at ({x}, {y})")
    return jsonify(result)


@app.route("/api/mouse/drag", methods=["POST"])
@require_api_key
def mouse_drag():
    """Drag from start to end position."""
    data = get_json()
    start_x = data.get("start_x", 0)
    start_y = data.get("start_y", 0)
    end_x = data.get("end_x", 0)
    end_y = data.get("end_y", 0)
    duration = data.get("duration", 0.2)
    button = data.get("button", "left")
    # Move to start first
    mouse_control.move_to(start_x, start_y)
    result = mouse_control.drag_to(end_x, end_y, duration, button)
    logger.debug(f"Mouse drag ({start_x},{start_y}) -> ({end_x},{end_y})")
    return jsonify(result)


@app.route("/api/mouse/scroll", methods=["POST"])
@require_api_key
def mouse_scroll():
    """Scroll wheel."""
    data = get_json()
    clicks = data.get("clicks", 0)
    x = data.get("x")
    y = data.get("y")
    result = mouse_control.scroll(clicks, x, y)
    logger.debug(f"Mouse scroll {clicks} at ({x}, {y})")
    return jsonify(result)

# ============================================================
# Keyboard Routes
# ============================================================

@app.route("/api/keyboard/type", methods=["POST"])
@require_api_key
def keyboard_type():
    """Type text string."""
    data = get_json()
    text = data.get("text", "")
    interval = data.get("interval", 0)
    result = keyboard_control.type_text(text, interval)
    logger.debug(f"Keyboard type: {text[:50]}...")
    return jsonify(result)


@app.route("/api/keyboard/press", methods=["POST"])
@require_api_key
def keyboard_press():
    """Press a single key."""
    data = get_json()
    key = data.get("key", "")
    result = keyboard_control.press_key(key)
    logger.debug(f"Keyboard press: {key}")
    return jsonify(result)


@app.route("/api/keyboard/hotkey", methods=["POST"])
@require_api_key
def keyboard_hotkey():
    """Press key combination."""
    data = get_json()
    keys = data.get("keys", [])
    result = keyboard_control.hotkey(*keys)
    logger.debug(f"Keyboard hotkey: {'+'.join(keys)}")
    return jsonify(result)


@app.route("/api/keyboard/key_down", methods=["POST"])
@require_api_key
def keyboard_key_down():
    """Hold key down."""
    data = get_json()
    key = data.get("key", "")
    result = keyboard_control.key_down(key)
    logger.debug(f"Keyboard key down: {key}")
    return jsonify(result)


@app.route("/api/keyboard/key_up", methods=["POST"])
@require_api_key
def keyboard_key_up():
    """Release key."""
    data = get_json()
    key = data.get("key", "")
    result = keyboard_control.key_up(key)
    logger.debug(f"Keyboard key up: {key}")
    return jsonify(result)


@app.route("/api/keyboard/write_instant", methods=["POST"])
@require_api_key
def keyboard_write_instant():
    """Paste text via clipboard (fast)."""
    data = get_json()
    text = data.get("text", "")
    result = keyboard_control.write_instant(text)
    logger.debug(f"Keyboard write instant: {text[:50]}...")
    return jsonify(result)

# ============================================================
# Screenshot Routes
# ============================================================

@app.route("/api/screenshot", methods=["GET"])
@require_api_key
def screenshot_full():
    """Capture full screenshot as base64."""
    quality = request.args.get("quality", config.SCREENSHOT_QUALITY, type=int)
    fmt = request.args.get("format", "base64")
    
    if fmt == "base64":
        image_data = screenshot.capture_to_base64(quality=quality)
        return jsonify({"success": True, "image": image_data, "format": "jpeg"})
    else:
        return jsonify({"success": False, "error": "Use format=base64"})


@app.route("/api/screenshot/region", methods=["POST"])
@require_api_key
def screenshot_region():
    """Capture region screenshot as base64."""
    data = get_json()
    x = data.get("x", 0)
    y = data.get("y", 0)
    width = data.get("width", 500)
    height = data.get("height", 500)
    quality = data.get("quality", config.SCREENSHOT_QUALITY)

    image = screenshot.capture_region(x, y, width, height)
    image_data = screenshot.capture_to_base64(image, quality=quality)
    return jsonify({"success": True, "image": image_data, "format": "jpeg"})


@app.route("/api/screenshot/file", methods=["POST"])
@require_api_key
def screenshot_file():
    """Save screenshot to file."""
    data = get_json()
    path = data.get("path", os.path.join(BASE_DIR, "screenshot.png"))
    result = screenshot.capture_to_file(path)
    return jsonify(result)


@app.route("/api/pixel", methods=["GET"])
@require_api_key
def pixel_color():
    """Get pixel color at coordinate."""
    x = request.args.get("x", 0, type=int)
    y = request.args.get("y", 0, type=int)
    result = screenshot.get_pixel_color(x, y)
    return jsonify(result)

# ============================================================
# Window Routes
# ============================================================

@app.route("/api/windows/list", methods=["GET"])
@require_api_key
def windows_list():
    """List all visible windows."""
    windows = window_manager.list_windows()
    return jsonify({"success": True, "windows": windows, "count": len(windows)})


@app.route("/api/windows/active", methods=["GET"])
@require_api_key
def windows_active():
    """Get currently active window."""
    result = window_manager.get_active_window()
    return jsonify({"success": True, "window": result})


@app.route("/api/windows/focus", methods=["POST"])
@require_api_key
def windows_focus():
    """Focus a window by hwnd or title."""
    data = get_json()
    hwnd = data.get("hwnd")
    title = data.get("title")
    result = window_manager.focus_window(hwnd=hwnd, title=title)
    logger.debug(f"Window focus: hwnd={hwnd} title={title}")
    return jsonify(result)


@app.route("/api/windows/minimize", methods=["POST"])
@require_api_key
def windows_minimize():
    """Minimize a window."""
    data = get_json()
    hwnd = data.get("hwnd")
    title = data.get("title")
    result = window_manager.minimize_window(hwnd=hwnd, title=title)
    return jsonify(result)


@app.route("/api/windows/maximize", methods=["POST"])
@require_api_key
def windows_maximize():
    """Maximize a window."""
    data = get_json()
    hwnd = data.get("hwnd")
    title = data.get("title")
    result = window_manager.maximize_window(hwnd=hwnd, title=title)
    return jsonify(result)


@app.route("/api/windows/restore", methods=["POST"])
@require_api_key
def windows_restore():
    """Restore a window."""
    data = get_json()
    hwnd = data.get("hwnd")
    title = data.get("title")
    result = window_manager.restore_window(hwnd=hwnd, title=title)
    return jsonify(result)


@app.route("/api/windows/close", methods=["POST"])
@require_api_key
def windows_close():
    """Close a window."""
    data = get_json()
    hwnd = data.get("hwnd")
    title = data.get("title")
    result = window_manager.close_window(hwnd=hwnd, title=title)
    logger.info(f"Window close: hwnd={hwnd} title={title}")
    return jsonify(result)


@app.route("/api/windows/move", methods=["POST"])
@require_api_key
def windows_move():
    """Move a window."""
    data = get_json()
    hwnd = data.get("hwnd")
    x = data.get("x", 0)
    y = data.get("y", 0)
    result = window_manager.move_window(hwnd, x, y)
    return jsonify(result)


@app.route("/api/windows/resize", methods=["POST"])
@require_api_key
def windows_resize():
    """Resize a window."""
    data = get_json()
    hwnd = data.get("hwnd")
    width = data.get("width", 800)
    height = data.get("height", 600)
    result = window_manager.resize_window(hwnd, width, height)
    return jsonify(result)


@app.route("/api/windows/find", methods=["GET"])
@require_api_key
def windows_find():
    """Find window by title substring."""
    title = request.args.get("title", "")
    result = window_manager.find_window_by_title(title)
    return jsonify(result)


@app.route("/api/windows/wait", methods=["POST"])
@require_api_key
def windows_wait():
    """Wait for window to appear."""
    data = get_json()
    title = data.get("title", "")
    timeout = data.get("timeout", 10)
    result = window_manager.wait_for_window(title, timeout)
    return jsonify(result)

# ============================================================
# Clipboard Routes
# ============================================================

@app.route("/api/clipboard", methods=["GET"])
@require_api_key
def clipboard_get():
    """Get clipboard text."""
    result = clipboard.get_text()
    return jsonify(result)


@app.route("/api/clipboard", methods=["POST"])
@require_api_key
def clipboard_set():
    """Set clipboard text."""
    data = get_json()
    text = data.get("text", "")
    result = clipboard.set_text(text)
    return jsonify(result)


@app.route("/api/clipboard/clear", methods=["POST"])
@require_api_key
def clipboard_clear():
    """Clear clipboard."""
    result = clipboard.clear()
    return jsonify(result)


@app.route("/api/clipboard/image", methods=["GET"])
@require_api_key
def clipboard_image():
    """Get clipboard image as base64."""
    result = clipboard.get_image()
    return jsonify(result)

# ============================================================
# Combo Routes (efficiency - multiple actions in one call)
# ============================================================

@app.route("/api/combo/click_and_type", methods=["POST"])
@require_api_key
def combo_click_and_type():
    """Click at position then type text."""
    data = get_json()
    x = data.get("x")
    y = data.get("y")
    text = data.get("text", "")
    interval = data.get("interval", 0)
    clear_first = data.get("clear_first", False)

    if x is not None and y is not None:
        mouse_control.click(x, y)
    
    if clear_first:
        keyboard_control.hotkey("ctrl", "a")
        time.sleep(0.02)

    keyboard_control.type_text(text, interval)
    logger.debug(f"Combo click+type at ({x},{y}): {text[:50]}...")
    return jsonify({"success": True})


@app.route("/api/combo/batch", methods=["POST"])
@require_api_key
def combo_batch():
    """Execute multiple actions in sequence.
    
    Body: {"actions": [
        {"type": "click", "x": 100, "y": 200},
        {"type": "type", "text": "hello"},
        {"type": "press", "key": "enter"},
        {"type": "sleep", "ms": 100},
        {"type": "hotkey", "keys": ["ctrl", "s"]},
        {"type": "move", "x": 300, "y": 400},
        {"type": "screenshot"},
    ]}
    """
    data = get_json()
    actions = data.get("actions", [])
    results = []

    for i, action in enumerate(actions):
        try:
            action_type = action.get("type", "")

            if action_type == "click":
                r = mouse_control.click(
                    action.get("x"), action.get("y"),
                    action.get("button", "left"), action.get("clicks", 1)
                )
            elif action_type == "double_click":
                r = mouse_control.double_click(action.get("x"), action.get("y"))
            elif action_type == "right_click":
                r = mouse_control.right_click(action.get("x"), action.get("y"))
            elif action_type == "move":
                r = mouse_control.move_to(
                    action.get("x", 0), action.get("y", 0),
                    action.get("duration", 0)
                )
            elif action_type == "scroll":
                r = mouse_control.scroll(
                    action.get("clicks", 0), action.get("x"), action.get("y")
                )
            elif action_type == "type":
                r = keyboard_control.type_text(
                    action.get("text", ""), action.get("interval", 0)
                )
            elif action_type == "write_instant":
                r = keyboard_control.write_instant(action.get("text", ""))
            elif action_type == "press":
                r = keyboard_control.press_key(action.get("key", ""))
            elif action_type == "hotkey":
                r = keyboard_control.hotkey(*action.get("keys", []))
            elif action_type == "key_down":
                r = keyboard_control.key_down(action.get("key", ""))
            elif action_type == "key_up":
                r = keyboard_control.key_up(action.get("key", ""))
            elif action_type == "sleep":
                ms = action.get("ms", 100)
                time.sleep(ms / 1000)
                r = {"success": True, "slept_ms": ms}
            elif action_type == "screenshot":
                quality = action.get("quality", config.SCREENSHOT_QUALITY)
                image_data = screenshot.capture_to_base64(quality=quality)
                r = {"success": True, "image": image_data}
            elif action_type == "focus":
                r = window_manager.focus_window(
                    hwnd=action.get("hwnd"), title=action.get("title")
                )
            else:
                r = {"success": False, "error": f"Unknown action type: {action_type}"}

            results.append({"index": i, **r})

        except Exception as e:
            results.append({"index": i, "success": False, "error": str(e)})

    logger.debug(f"Batch executed {len(actions)} actions")
    return jsonify({"success": True, "results": results})

# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("PC Control Server starting...")
    logger.info(f"Base directory: {BASE_DIR}")
    logger.info(f"Listening on: http://{config.HOST}:{config.PORT}")
    logger.info(f"Auth: {'enabled' if config.API_KEY else 'disabled'}")
    
    screen = pyautogui.size()
    logger.info(f"Screen size: {screen[0]}x{screen[1]}")
    logger.info("=" * 60)

    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=False,
        threaded=True,
        use_reloader=False,
    )
