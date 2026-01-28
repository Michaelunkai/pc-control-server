@echo off
echo ============================================
echo  PC Control Server - Build Script
echo ============================================
echo.

cd /d "F:\study\Dev_Toolchain\programming\python\apps\pc-control-server"

echo [1/3] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)
echo.

echo [2/3] Running PyInstaller...
pyinstaller --onefile --noconsole --name pc-control-server ^
    --add-data "src;src" ^
    --hidden-import win32gui ^
    --hidden-import win32con ^
    --hidden-import win32process ^
    --hidden-import win32clipboard ^
    --hidden-import win32api ^
    --hidden-import pywintypes ^
    src\server.py
if errorlevel 1 (
    echo ERROR: PyInstaller build failed!
    pause
    exit /b 1
)
echo.

echo [3/3] Build complete!
echo.
echo EXE location:
echo   F:\study\Dev_Toolchain\programming\python\apps\pc-control-server\dist\pc-control-server.exe
echo.
pause
