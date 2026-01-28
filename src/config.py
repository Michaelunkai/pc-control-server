"""Configuration settings for PC Control Server."""

# Server settings
HOST = "127.0.0.1"  # Localhost only - no external access
PORT = 5000
API_KEY = None  # Set to a string to enable authentication (e.g., "my-secret-key")

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/server.log"

# Screenshot settings
SCREENSHOT_FORMAT = "JPEG"
SCREENSHOT_QUALITY = 85

# pyautogui settings
FAILSAFE = False  # Disable failsafe (moving mouse to corner won't stop)
PAUSE = 0.0  # No delay between pyautogui actions (maximum speed)

# Screen info (auto-detected at startup)
SCREEN_WIDTH = None
SCREEN_HEIGHT = None
