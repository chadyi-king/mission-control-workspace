@echo off
echo ============================================
echo  SETUP AUTO-START ON WINDOWS BOOT
echo ============================================
echo.
echo This will make the agent start automatically when Windows boots.
echo You can still stop it anytime by closing the window.
echo.
echo Options:
echo [1] Enable auto-start (starts on every boot)
echo [2] Disable auto-start
echo [3] Cancel
choice /c 123 /m "Choose option"

if errorlevel 3 goto :cancel
if errorlevel 2 goto :disable
if errorlevel 1 goto :enable

:enable
echo.
echo Creating startup shortcut...
copy "C:\DesktopControlAgent\START-EVERYTHING.bat" "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\" > nul
echo ✅ Auto-start ENABLED
echo The agent will start automatically when Windows boots.
echo.
pause
goto :end

:disable
echo.
echo Removing startup shortcut...
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\START-EVERYTHING.bat" > nul 2>&1
echo ✅ Auto-start DISABLED
echo The agent will NOT start automatically.
echo.
pause
goto :end

:cancel
echo Cancelled.

:end
