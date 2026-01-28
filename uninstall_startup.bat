@echo off
echo ============================================
echo  PC Control Server - Remove from Startup
echo ============================================
echo.

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_NAME=PC Control Server.lnk"

if exist "%STARTUP_FOLDER%\%SHORTCUT_NAME%" (
    del "%STARTUP_FOLDER%\%SHORTCUT_NAME%"
    echo Startup shortcut removed successfully.
) else (
    echo No startup shortcut found - nothing to remove.
)

echo.
pause
