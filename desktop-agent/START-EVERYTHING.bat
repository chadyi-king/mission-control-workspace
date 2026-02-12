@echo off
chcp 65001 > nul
echo ============================================
echo  MISSION CONTROL - DESKTOP AGENT STARTER
echo ============================================
echo.
echo This will start EVERYTHING needed for remote control:
echo  • Desktop Control Agent (screenshots, mouse, keyboard)
echo  • ngrok tunnel (secure connection)
echo  • Show you the connection URL
echo.
echo Press any key to start...
pause > nul
cls

echo [1/4] Checking Python...
py --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.14 first.
    echo Download: https://python.org
    pause
    exit /b 1
)
echo ✅ Python found

echo.
echo [2/4] Checking ngrok...
ngrok --version > nul 2>&1
if errorlevel 1 (
    echo ❌ ngrok not found! Installing now...
    winget install ngrok.ngrok --accept-source-agreements --accept-package-agreements
    if errorlevel 1 (
        echo ❌ Failed to install ngrok. Please install manually.
        pause
        exit /b 1
    )
)
echo ✅ ngrok found

echo.
echo [3/4] Checking Desktop Control Agent...
if not exist "C:\DesktopControlAgent\agent.py" (
    echo ❌ Agent not found! Installing now...
    mkdir "C:\DesktopControlAgent" 2> nul
    echo Downloading agent files...
    curl -L -o "C:\DesktopControlAgent\agent.py" "https://raw.githubusercontent.com/chadyi-king/mission-control/main/agent.py"
    curl -L -o "C:\DesktopControlAgent\requirements.txt" "https://raw.githubusercontent.com/chadyi-king/mission-control/main/requirements.txt"
    echo Installing Python packages...
    py -m pip install -r "C:\DesktopControlAgent\requirements.txt" -q
)
echo ✅ Agent ready

echo.
echo [4/4] Starting services...
echo.
echo ============================================
echo  STARTING DESKTOP CONTROL AGENT
echo ============================================
start "Desktop Control Agent" cmd /k "cd /d C:\DesktopControlAgent && py agent.py"

echo ⏳ Waiting 5 seconds for agent to start...
timeout /t 5 /nobreak > nul

echo.
echo ============================================
echo  STARTING NGROK TUNNEL
echo ============================================
echo When ngrok starts, COPY THE HTTPS URL and give it to CHAD_YI
echo.
echo The URL looks like: https://abc123.ngrok.io
echo.
echo Press Ctrl+C in this window to stop everything.
echo ============================================
echo.
ngrok http 5000

echo.
echo ============================================
echo  AGENT STOPPED
echo ============================================
echo To restart, just double-click this file again.
echo.
pause
