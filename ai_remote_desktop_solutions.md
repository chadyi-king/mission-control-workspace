# AI Remote Desktop Solutions - Practical Setup Guide

## Overview

This document provides working solutions to let an AI assistant see and control a user's desktop remotely. Solutions range from simple Python scripts to full remote desktop systems.

---

## SOLUTION 1: RemoteUse (MCP Server) ⭐ RECOMMENDED
**Best for:** AI assistants using MCP protocol (Claude Desktop, etc.)

### What it is
An MCP (Model Context Protocol) server that exposes 12 semantic desktop control actions to AI agents. Perfect for Claude, GPT-4, or any MCP-compatible AI.

### Features
- ✅ 12 semantic actions (click, type, scroll, drag, screenshot)
- ✅ Vision-first design - AI sees screen, decides actions
- ✅ Cross-platform (Windows, macOS, Linux)
- ✅ Ultra-fast screenshots (16-47ms using mss library)
- ✅ Safety mechanisms (auto-releases stuck keys)
- ✅ Works with Claude Desktop out of the box

### Setup Steps

```bash
# 1. Clone and install
git clone https://github.com/BryanTheLai/anydesk-agent.git
cd anydesk-agent
pip install -r requirements.txt

# 2. Run the MCP server
python -m remoteuse.server.mcp_server

# 3. Configure Claude Desktop
# Edit: ~/Library/Application Support/Claude/claude_desktop_config.json (Mac)
# Or: %APPDATA%\Claude\claude_desktop_config.json (Windows)
```

Add this configuration:
```json
{
  "mcpServers": {
    "remoteuse": {
      "command": "python",
      "args": ["-m", "remoteuse.server.mcp_server"]
    }
  }
}
```

### Usage Example
```
User: "Screenshot my desktop"
AI: [calls screenshot() tool]
AI: "I can see Chrome and VS Code open."

User: "Open Notepad and type 'Hello AI'"
AI: [calls click_at(), type_text(), etc.]
AI: "Done!"
```

### Available Actions
- `screenshot(monitor)` - Capture screen as base64 PNG
- `click_at(x, y, button, count)` - Click operations
- `type_text(text)` / `type_text_at(x, y, text)` - Text input
- `key_press(key)` / `key_combination(keys)` - Keyboard shortcuts
- `hover_at(x, y)` - Mouse hover
- `drag_and_drop(from_x, from_y, to_x, to_y)` - Drag operations
- `scroll_at(x, y, direction, amount)` - Scrolling
- `wait(duration_ms)` - Timing control

---

## SOLUTION 2: Python + PyAutoGUI + MSS (DIY Approach)
**Best for:** Custom solutions, WSL2 compatibility, full control

### What it is
A lightweight Python-based solution using `pyautogui` for control and `mss` for screenshots.

### Setup Steps

```bash
# Install dependencies
pip install pyautogui mss pynput pillow

# For WSL2: You'll need an X server like VcXsrv or WSLg (Windows 11)
```

### Basic Implementation
```python
import pyautogui
import mss
import mss.tools
import time
import base64
from io import BytesIO

class DesktopController:
    def __init__(self):
        self.sct = mss.mss()
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = 0.1
    
    def screenshot(self, monitor=1):
        """Capture screen and return base64 PNG"""
        monitor_obj = self.sct.monitors[monitor]
        screenshot = self.sct.grab(monitor_obj)
        img_bytes = mss.tools.to_png(screenshot.rgb, screenshot.size)
        return base64.b64encode(img_bytes).decode()
    
    def click(self, x, y, button='left', clicks=1):
        """Click at coordinates"""
        pyautogui.click(x, y, button=button, clicks=clicks)
    
    def type_text(self, text, interval=0.01):
        """Type text"""
        pyautogui.typewrite(text, interval=interval)
    
    def key_press(self, key):
        """Press a key"""
        pyautogui.press(key)
    
    def key_combo(self, *keys):
        """Press key combination (e.g., ctrl+c)"""
        pyautogui.hotkey(*keys)
    
    def move_mouse(self, x, y):
        """Move mouse to coordinates"""
        pyautogui.moveTo(x, y)
    
    def scroll(self, amount, x=None, y=None):
        """Scroll (positive=up, negative=down)"""
        if x and y:
            pyautogui.scroll(amount, x, y)
        else:
            pyautogui.scroll(amount)

# Auto-screenshot every 5 seconds example
controller = DesktopController()
while True:
    img_b64 = controller.screenshot()
    # Send to AI for analysis
    time.sleep(5)
```

### Pros
- Works in WSL2 with X server
- Full control over implementation
- No external dependencies
- Can integrate with any AI system

### Cons
- Requires X server on WSL2
- Need to build your own API/interface

---

## SOLUTION 3: VNC-Based Solutions (vncdotool)
**Best for:** Existing VNC infrastructure, headless systems

### What it is
`vncdotool` is a command-line VNC client and Python library for automating VNC sessions.

### Setup Steps

```bash
# 1. Install vncdotool
pip install vncdotool

# 2. Install a VNC server on target machine
# Windows: TightVNC, RealVNC, or UltraVNC
# Linux: x11vnc or TigerVNC
# Mac: Built-in Screen Sharing (VNC compatible)
```

### VNC Server Setup

**Windows (TightVNC):**
1. Download from https://www.tightvnc.com/
2. Install server component
3. Set password
4. Note the IP and port (default: 5900)

**Linux (x11vnc):**
```bash
# Install
sudo apt install x11vnc

# Set password
x11vnc -storepasswd

# Start server
x11vnc -forever -usepw -display :0
```

### Usage Examples
```bash
# Type text
vncdo -s 192.168.1.100 type "hello world"

# Take screenshot
vncdo -s 192.168.1.100 capture screen.png

# Click and type
vncdo -s 192.168.1.100 click 100 200
vncdo -s 192.168.1.100 type "username"
vncdo -s 192.168.1.100 key press tab
vncdo -s 192.168.1.100 type "password"
vncdo -s 192.168.1.100 key press enter
```

### Python API
```python
from vncdotool import api

client = api.connect('192.168.1.100', password='yourpassword')
client.captureScreen('screenshot.png')
client.mouseMove(100, 200)
client.mousePress(1)  # Left click
client.typewrite("Hello AI")
client.keyPress('enter')
client.disconnect()
```

### Pros
- Works across network
- Mature, stable protocol
- Many server options
- Headless compatible

### Cons
- Requires VNC server running
- Additional setup complexity
- Not ideal for local-only use

---

## SOLUTION 4: IntelCLaw (Full AI Agent System)
**Best for:** Windows users wanting a complete AI assistant

### What it is
A full autonomous AI agent for Windows with screen understanding, task automation, and persistent memory.

### Features
- 🤖 REACT Agent Architecture (LangChain/LangGraph)
- 👁️ Real-time screen capture, OCR, UI recognition
- 🧠 Persistent memory (SQLite) with secret redaction
- 📄 PDF RAG support
- 💻 PowerShell integration
- 🖥️ Transparent overlay UI (Ctrl+Shift+Space)
- 🌐 WebSocket gateway (localhost:8765)

### Setup Steps

```bash
# 1. Install uv (package manager)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. Clone repository
git clone https://github.com/0x-Professor/IntelCLaw.git
cd IntelCLaw

# 3. Set up environment
copy .env.example .env
# Edit .env with your API keys (OpenAI, etc.)

# 4. Install dependencies
uv sync

# 5. Install Tesseract OCR
# Download from: https://github.com/UB-Mannheim/tesseract/wiki

# 6. Run
uv run python main.py
```

### Configuration
Edit `config.yaml`:
```yaml
models:
  primary: gpt-4o
  fallback: gpt-4o-mini

privacy:
  screen_capture: true
  track_keyboard: false
  excluded_windows:
    - "*password*"
    - "*bank*"

hotkeys:
  summon: ctrl+shift+space
```

### Pros
- Complete solution out of the box
- Persistent memory
- Privacy controls
- Extensible with MCP

### Cons
- Windows only
- Requires API keys
- Heavier resource usage

---

## SOLUTION 5: PyGPT (Open Source Desktop AI)
**Best for:** Cross-platform desktop AI assistant

### What it is
An open-source desktop AI assistant for Windows, macOS, and Linux with vision capabilities and tool integration.

### Features
- 12 modes: Chat, Vision, Agents, Computer Use, etc.
- Real-time video camera capture
- Image analysis via vision models
- System command execution
- Python code interpreter
- MCP support

### Installation

```bash
# PyPi
pip install pygpt-net

# Or download binaries from:
# https://pygpt.net/
```

### Vision Mode Usage
1. Launch PyGPT
2. Switch to "Vision" mode
3. Enable camera or screen capture
4. AI can now see and analyze your screen

### Pros
- Cross-platform
- No coding required
- Multiple AI model support
- Active development

### Cons
- GUI-based (less automatable)
- May need configuration for remote control

---

## SOLUTION 6: Mira Screen Share (Rust-based)
**Best for:** High-performance screen sharing with remote control

### What it is
A high-performance screen-sharing/remote collaboration tool written in Rust with WebRTC.

### Features
- 60 FPS encoding at 4K
- 110ms E2E latency
- Remote mouse/keyboard control
- System audio capture
- Cross-platform (macOS, Windows)
- P2P connection (or TURN relay)

### Setup
```bash
# Download pre-compiled binaries:
# https://github.com/mira-screen-share/sharer/releases

# Or build from source:
# Install ffmpeg, then:
cargo run --release
```

### Usage
1. Run sharer on host machine
2. Viewer connects via browser at mirashare.app
3. Share the connection code
4. Viewer can see and control the screen

### Pros
- High performance
- WebRTC (low latency)
- Browser-based viewer
- Open source

### Cons
- Self-hosted TURN server recommended
- Still in early development
- Not specifically built for AI integration

---

## SOLUTION 7: PairUX (Collaborative Screen Sharing)
**Best for:** Collaborative remote control with AI integration potential

### What it is
Open-source collaborative screen sharing with simultaneous remote control (like Screenhero).

### Features
- Remote mouse + keyboard control
- Simultaneous input (host and viewer)
- E2E encryption
- PWA viewer (works in browser)
- Cross-platform

### Installation
```bash
# Via Homebrew (Mac)
brew install pairux

# Via WinGet (Windows)
winget install PairUX

# Or build from source:
git clone https://github.com/profullstack/pairux.com
cd pairux.com
npm install
npm run build
```

### Pros
- Easy to install
- Browser-based viewer
- Good for collaboration
- Open source

### Cons
- Requires explicit host approval for control
- Not specifically designed for AI

---

## WSL2-Specific Considerations

### For GUI Applications in WSL2

**Option A: WSLg (Windows 11)**
- Built-in, no setup needed
- GUI apps work out of the box

**Option B: VcXsrv (Windows 10)**
1. Download and install VcXsrv
2. Run XLaunch with "Disable access control"
3. In WSL2: `export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0`

**Option C: WSL2 with VNC**
1. Install TigerVNC in WSL2: `sudo apt install tigervnc-standalone-server`
2. Start VNC server: `vncserver :1 -geometry 1920x1080 -depth 24`
3. Connect from Windows using VNC viewer

### Running Python Automation from WSL2

```bash
# Install dependencies in WSL2
pip install pyautogui mss

# For WSL2 to control Windows host, use one of:
# 1. SSH into Windows and run commands
# 2. Use PowerShell remoting
# 3. Run the Python script directly on Windows
```

---

## COMPARISON TABLE

| Solution | Platform | AI Integration | Setup Difficulty | Latency | Cost |
|----------|----------|----------------|------------------|---------|------|
| RemoteUse | Win/Mac/Linux | Excellent (MCP) | Easy | Low | Free |
| PyAutoGUI DIY | Win/Mac/Linux | Manual | Medium | Low | Free |
| VNC/vncdotool | Win/Mac/Linux | Manual | Medium | Medium | Free |
| IntelCLaw | Windows | Built-in | Medium | Low | Free + API |
| PyGPT | Win/Mac/Linux | Built-in | Easy | Low | Free + API |
| Mira | Win/Mac | Manual | Hard | Very Low | Free |
| PairUX | Win/Mac/Linux | Manual | Easy | Low | Free |

---

## RECOMMENDATIONS

### For Quick Setup Today
1. **Use RemoteUse** if you have Claude Desktop or MCP-compatible AI
2. **Use PyAutoGUI DIY** if you want custom integration
3. **Use PyGPT** if you want a complete GUI solution

### For Production/Enterprise
1. **VNC-based solution** for stability and network access
2. **IntelCLaw** for Windows automation
3. **Build custom** with PyAutoGUI + FastAPI for web API

### For WSL2 Specifically
- Run Python automation scripts on Windows side (not WSL2)
- Use SSH or PowerShell remoting from WSL2 to control Windows
- Or use VNC for full remote control

---

## SECURITY WARNINGS

⚠️ All these solutions grant significant control over the desktop:
- Only use with trusted AI systems
- Use privacy filters to exclude sensitive windows
- Consider running in a VM for untrusted AI
- Enable automatic key release mechanisms
- Never share VNC passwords publicly

---

## SAMPLE INTEGRATION CODE

### FastAPI + PyAutoGUI (Web API for AI)
```python
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import base64
import pyautogui
import mss

app = FastAPI()
controller = DesktopController()

@app.post("/screenshot")
def screenshot():
    img_b64 = controller.screenshot()
    return {"image": img_b64}

@app.post("/click")
def click(x: int, y: int):
    controller.click(x, y)
    return {"status": "ok"}

@app.post("/type")
def type_text(text: str):
    controller.type_text(text)
    return {"status": "ok"}

# Run with: uvicorn main:app --host 0.0.0.0 --port 8000
```

This API can be called by any AI system to control the desktop remotely.

---

## RESOURCES

- **RemoteUse**: https://github.com/BryanTheLai/anydesk-agent
- **vncdotool**: https://github.com/sibson/vncdotool
- **IntelCLaw**: https://github.com/0x-Professor/IntelCLaw
- **PyGPT**: https://pygpt.net/
- **Mira**: https://github.com/mira-screen-share/sharer
- **PairUX**: https://github.com/profullstack/pairux.com
- **PyAutoGUI**: https://pyautogui.readthedocs.io/
- **MSS**: https://github.com/BoboTiG/python-mss
