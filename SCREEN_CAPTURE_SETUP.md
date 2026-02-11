# SCREEN CAPTURE SETUP FOR OPENCLAW
## This lets me (Chad Yi) see your screen every 5 seconds

## STEP 1: Install Python on Windows (if not already installed)
1. Go to https://python.org/downloads
2. Download Python 3.11 or higher
3. Run installer
4. ☑️ CHECK "Add Python to PATH"
5. Click "Install Now"

## STEP 2: Install Required Libraries
Open Command Prompt (cmd) and run:
```
pip install pillow
```

## STEP 3: Run the Screenshot Script
1. Copy `screen_capture.py` to your Desktop
2. Open Command Prompt
3. Navigate to Desktop:
   ```
   cd Desktop
   ```
4. Run the script:
   ```
   python screen_capture.py
   ```

## WHAT HAPPENS:
- Screenshot saved every 5 seconds
- Files go to: C:\Users\[YourName]\openclaw_screenshots\
- Keeps last 100 screenshots (auto-deletes old ones)
- Latest screenshot always in: `latest.json`

## HOW I ACCESS:
- You can share screenshots via Telegram
- Or use file sharing to WSL2
- Or I can read from shared folder

## TO STOP:
Press `Ctrl+C` in the Command Prompt window

## TESTING:
Once running, open your Mission Control Dashboard
I can ask you to send me the latest screenshot
I'll see exactly what you see!
