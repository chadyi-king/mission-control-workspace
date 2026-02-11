# Desktop Control Agent - Setup Instructions

## What This Does

This agent lets CHAD_YI (me) control your Windows PC remotely to:
- Open Chrome and access websites
- Control Telegram Desktop
- Trade on OANDA or other platforms
- Access Google Drive
- Search YouTube
- Basically anything a human can do with mouse and keyboard

## SAFETY FIRST

**To stop me instantly:**
- Move your mouse to any **screen corner** (failsafe)
- Close the agent window (Ctrl+C)
- I can only click/type - cannot delete files or run dangerous commands

## Installation Steps

### Step 1: Copy Files
Copy these files to `C:\DesktopControlAgent\`:
- `agent.py`
- `start.bat`
- `install.bat`

### Step 2: Install Dependencies
Double-click `install.bat`
This installs required Python packages.

### Step 3: Start the Agent
Double-click `start.bat`

### Step 4: Open Browser
Go to: http://localhost:5000

You should see the control interface with your live screenshot.

## How It Works

1. **You start the agent** on your PC
2. **I connect** to http://your-pc-ip:5000
3. **I can:**
   - See your screen (screenshots)
   - Move your mouse
   - Click at specific coordinates
   - Type text
   - Press keys (Enter, Tab, etc.)
4. **You watch** everything happen on your screen

## Example Use Cases

### Trading Bot
1. You keep Telegram Desktop open with signals
2. I monitor screenshots
3. See "BUY XAUUSD 2680" signal
4. Open OANDA, click Buy, set stop loss
5. Log trade to dashboard

### Story Writing
1. Open Google Docs
2. I type the story based on your outline
3. You review and edit

### YouTube Research
1. Open Chrome
2. I search YouTube for topics
3. Copy transcripts for script writing

## Troubleshooting

**"Python not found"**
- Make sure you installed Python 3.14
- Try using `py` instead of `python`

**"Port 5000 already in use"**
- Another program is using that port
- Close other apps or restart PC

**"Cannot take screenshot"**
- Windows may block it
- Run as Administrator if needed

**Agent not responding**
- Check the logs in browser: http://localhost:5000
- Restart the agent

## Security Notes

- Agent only runs when YOU start it
- All communication is local (your PC only)
- I cannot access files or run system commands
- You can stop me anytime by moving mouse to corner

## Files Created

- `C:\DesktopControlAgent\agent.py` - Main program
- `C:\DesktopControlAgent\logs\agent.log` - Activity log
- `C:\DesktopControlAgent\screenshots\` - Screenshots taken

## Support

If something breaks, tell me and I'll fix the code.
