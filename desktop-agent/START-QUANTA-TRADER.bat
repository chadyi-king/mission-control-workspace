@echo off
echo ============================================
echo  QUANTA TRADER - AUTO START
echo ============================================
echo.
echo Starting automated trading system...
echo.
echo This will:
echo  1. Start TeamViewer Host (remote access)
echo  2. Start Quanta Trader (signal detection + trading)
echo  3. Monitor CallistoFx every 1 second
echo  4. Auto-execute trades on OANDA
echo.
echo Account: $2,000
-echo Risk: 2%% per trade ($40 max)
echo Scan: Every 1 second
echo.
echo Press any key to start...
pause > nul
cls

echo [1/3] Checking TeamViewer...
tasklist | findstr "TeamViewer" > nul
if errorlevel 1 (
    echo Starting TeamViewer Host...
    start "" "C:\Program Files\TeamViewer\TeamViewer.exe"
    timeout /t 3 > nul
) else (
    echo ✅ TeamViewer already running
)

echo.
echo [2/3] Checking Ollama (for local AI)...
ollama --version > nul 2>&1
if errorlevel 1 (
    echo ⚠️ Ollama not found. Quanta will use API fallback.
) else (
    echo ✅ Ollama found
)

echo.
echo [3/3] Starting Quanta Trader...
cd /d C:\DesktopControlAgent
echo.
echo ⚠️ IMPORTANT: Update API keys in quanta_trader.py first!
echo.
echo Starting in 5 seconds...
timeout /t 5 > nul

py quanta_trader.py

echo.
echo ============================================
echo  QUANTA TRADER STOPPED
echo ============================================
echo.
echo To restart, double-click this file again.
echo.
pause
