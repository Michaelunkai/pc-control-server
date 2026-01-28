@echo off
echo ============================================
echo  PC Control Server - Install to Startup
echo ============================================
echo.

set "EXE_PATH=F:\study\Dev_Toolchain\programming\python\apps\pc-control-server\dist\pc-control-server.exe"
set "WORK_DIR=F:\study\Dev_Toolchain\programming\python\apps\pc-control-server"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_NAME=PC Control Server.lnk"

echo Checking if EXE exists...
if not exist "%EXE_PATH%" (
    echo ERROR: EXE not found at:
    echo   %EXE_PATH%
    echo.
    echo Please run build.bat first!
    pause
    exit /b 1
)

echo Creating startup shortcut...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTUP_FOLDER%\%SHORTCUT_NAME%'); $s.TargetPath = '%EXE_PATH%'; $s.WorkingDirectory = '%WORK_DIR%'; $s.Description = 'PC Remote Control Server - localhost:5000'; $s.Save()"

if errorlevel 1 (
    echo ERROR: Failed to create shortcut!
    pause
    exit /b 1
)

echo.
echo SUCCESS! Startup shortcut created at:
echo   %STARTUP_FOLDER%\%SHORTCUT_NAME%
echo.
echo The server will now start automatically when Windows boots.
echo.
pause
