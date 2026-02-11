@echo off
echo ========================================
echo Starting Desktop Control Agent + ngrok
echo ========================================
echo.

REM Check if agent exists
if not exist "C:\DesktopControlAgent\agent.py" (
    echo ERROR: Agent not found in C:\DesktopControlAgent\
    echo Please install agent first.
    pause
    exit /b 1
)

REM Check if ngrok is installed
ngrok --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: ngrok not found. Please install ngrok first.
    echo winget install ngrok.ngrok
    pause
    exit /b 1
)

echo Starting Desktop Control Agent...
echo.

REM Start agent in new window
cd /d C:\DesktopControlAgent
start "Desktop Control Agent" cmd /k "py agent.py"

echo Waiting 5 seconds for agent to start...
timeout /t 5 /nobreak >nul

echo.
echo Starting ngrok tunnel...
echo.

REM Start ngrok in this window
ngrok http 5000

echo.
echo ========================================
echo Agent and ngrok stopped.
echo ========================================
pause
