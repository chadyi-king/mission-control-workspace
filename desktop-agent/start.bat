@echo off
echo Starting Desktop Control Agent...
echo.
echo ========================================
echo Desktop Control Agent v1.0.0
echo ========================================
echo.
echo This will:
echo - Start a web server on your PC
echo - Allow remote control of your desktop
echo - Open browser at http://localhost:5000
echo.
echo SAFETY:
echo - Move mouse to screen corner to stop instantly
echo - All actions are logged
echo - You can see everything happening
echo.
echo Press any key to start...
pause > nul

cd /d C:\DesktopControlAgent

REM Check if agent exists, if not copy from workspace
if not exist "agent.py" (
    echo ERROR: agent.py not found in C:\DesktopControlAgent
    echo Please run install.bat first
    pause
    exit /b 1
)

echo.
echo Starting agent...
echo Open browser: http://localhost:5000
echo.

py agent.py

echo.
echo Agent stopped.
pause
