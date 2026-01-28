# PC Control Server

Local HTTP API server for remote mouse, keyboard, screenshot, and window control.

## Quick Start

### Development
```batch
cd F:\study\Dev_Toolchain\programming\python\apps\pc-control-server
pip install -r requirements.txt
python src\server.py
```

### Build EXE
```batch
build.bat
```

### Install to Startup
```batch
install_startup.bat
```

## API Endpoints

Base URL: `http://127.0.0.1:5000`

### System
- `GET /api/health` - Health check
- `GET /api/screen/size` - Screen dimensions

### Mouse
- `GET /api/mouse/position` - Current mouse position
- `POST /api/mouse/move` - Move to `{x, y, duration}`
- `POST /api/mouse/move_relative` - Move relative `{dx, dy}`
- `POST /api/mouse/click` - Click `{x, y, button, clicks}`
- `POST /api/mouse/double_click` - Double click `{x, y}`
- `POST /api/mouse/right_click` - Right click `{x, y}`
- `POST /api/mouse/drag` - Drag `{start_x, start_y, end_x, end_y}`
- `POST /api/mouse/scroll` - Scroll `{clicks, x, y}`

### Keyboard
- `POST /api/keyboard/type` - Type text `{text, interval}`
- `POST /api/keyboard/press` - Press key `{key}`
- `POST /api/keyboard/hotkey` - Key combo `{keys: [...]}`
- `POST /api/keyboard/key_down` - Hold key `{key}`
- `POST /api/keyboard/key_up` - Release key `{key}`
- `POST /api/keyboard/write_instant` - Paste via clipboard `{text}`

### Screenshots
- `GET /api/screenshot` - Full screen base64 `?quality=85`
- `POST /api/screenshot/region` - Region `{x, y, width, height}`
- `POST /api/screenshot/file` - Save to file `{path}`
- `GET /api/pixel` - Pixel color `?x=0&y=0`

### Windows
- `GET /api/windows/list` - List all windows
- `GET /api/windows/active` - Active window info
- `POST /api/windows/focus` - Focus `{hwnd}` or `{title}`
- `POST /api/windows/minimize` - Minimize
- `POST /api/windows/maximize` - Maximize
- `POST /api/windows/restore` - Restore
- `POST /api/windows/close` - Close
- `POST /api/windows/move` - Move `{hwnd, x, y}`
- `POST /api/windows/resize` - Resize `{hwnd, width, height}`
- `GET /api/windows/find` - Find `?title=...`
- `POST /api/windows/wait` - Wait for window `{title, timeout}`

### Clipboard
- `GET /api/clipboard` - Get text
- `POST /api/clipboard` - Set text `{text}`
- `POST /api/clipboard/clear` - Clear
- `GET /api/clipboard/image` - Get image as base64

### Combo
- `POST /api/combo/click_and_type` - Click then type `{x, y, text}`
- `POST /api/combo/batch` - Multiple actions `{actions: [...]}`

## Security
- Binds to `127.0.0.1` only (no external access)
- Optional API key via `X-API-Key` header
