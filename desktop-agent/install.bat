@echo off
echo Installing Desktop Control Agent...
echo.

REM Check if Python is available
py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.14 first.
    pause
    exit /b 1
)

echo Python found:
py --version
echo.

REM Create directories
if not exist "C:\DesktopControlAgent" mkdir "C:\DesktopControlAgent"
if not exist "C:\DesktopControlAgent\logs" mkdir "C:\DesktopControlAgent\logs"
if not exist "C:\DesktopControlAgent\screenshots" mkdir "C:\DesktopControlAgent\screenshots"

echo Installing required packages...
py -m pip install flask pyautogui pillow websocket-client

echo.
echo Installation complete!
echo.
echo To start the agent, run: start.bat
pause
