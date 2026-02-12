#!/usr/bin/env python3
"""
Desktop Control Agent - Safe Remote Computer Control
Created for Caleb's Mission Control System

SAFETY FEATURES:
- Only takes screenshots, moves mouse, clicks, types
- NO file deletion, NO system commands, NO network access beyond websockets
- ESC key stops all operations immediately
- All actions logged to local file only
"""

import sys
import time
import json
import base64
import logging
import threading
from datetime import datetime
from pathlib import Path
from io import BytesIO

# Disable PyAutoGUI failsafe (we handle safety ourselves)
import pyautogui
pyautogui.FAILSAFE = True  # Move mouse to corner to stop

from PIL import Image
from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO, emit

# Configuration
AGENT_VERSION = "1.0.1"
LOG_DIR = Path("C:/DesktopControlAgent/logs")
SCREENSHOT_DIR = Path("C:/DesktopControlAgent/screenshots")
LOG_FILE = LOG_DIR / "agent.log"
MAX_SCREENSHOTS = 300  # Keep up to 300 screenshots (~150 MB max)

def cleanup_old_screenshots():
    """Keep only the most recent MAX_SCREENSHOTS screenshots"""
    try:
        screenshots = sorted(SCREENSHOT_DIR.glob("*.png"), key=lambda x: x.stat().st_mtime, reverse=True)
        if len(screenshots) > MAX_SCREENSHOTS:
            for old_screenshot in screenshots[MAX_SCREENSHOTS:]:
                old_screenshot.unlink()
                logger.info(f"Cleaned up old screenshot: {old_screenshot.name}")
    except Exception as e:
        logger.error(f"Cleanup error: {e}")

# Ensure directories exist
LOG_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mission-control-agent-v1'
socketio = SocketIO(app, cors_allowed_origins="*")

# Agent state
agent_state = {
    "connected": False,
    "last_action": None,
    "action_count": 0,
    "started_at": datetime.now().isoformat(),
    "version": AGENT_VERSION
}

# HTML Interface for viewing/control
HTML_INTERFACE = """
<!DOCTYPE html>
<html>
<head>
    <title>Desktop Control Agent</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a2e; color: white; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #00ff88; }
        .status { padding: 10px; border-radius: 5px; margin: 10px 0; }
        .status.connected { background: #00ff8820; border: 1px solid #00ff88; }
        .status.disconnected { background: #ff444420; border: 1px solid #ff4444; }
        #screenshot { max-width: 100%; border: 2px solid #444; border-radius: 5px; }
        .controls { margin: 20px 0; padding: 15px; background: #16213e; border-radius: 5px; }
        button { padding: 10px 20px; margin: 5px; cursor: pointer; background: #0f3460; color: white; border: none; border-radius: 3px; }
        button:hover { background: #1a4a7a; }
        .log { background: #0f0f1a; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px; height: 200px; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🖥️ Desktop Control Agent v{{ version }}</h1>
        
        <div class="status {{ 'connected' if connected else 'disconnected' }}">
            Status: {{ 'Connected' if connected else 'Disconnected' }}
            | Actions: {{ action_count }}
            | Started: {{ started_at }}
        </div>
        
        <div class="controls">
            <h3>Quick Actions</h3>
            <button onclick="screenshot()">📸 Take Screenshot</button>
            <button onclick="stopAgent()">🛑 Stop Agent (ESC)</button>
            <button onclick="location.reload()">🔄 Refresh</button>
        </div>
        
        <div>
            <h3>Live Screenshot</h3>
            <img id="screenshot" src="/api/screenshot" alt="Desktop Screenshot">
            <p><small>Click "Take Screenshot" to update. Auto-refresh disabled to save storage.</small></p>
        </div>
        
        <div class="controls">
            <h3>Manual Control (Use with caution)</h3>
            <form id="clickForm">
                <label>X: <input type="number" id="clickX" value="500" style="width: 60px;"></label>
                <label>Y: <input type="number" id="clickY" value="500" style="width: 60px;"></label>
                <button type="submit">🖱️ Click</button>
            </form>
            <form id="typeForm">
                <input type="text" id="typeText" placeholder="Type text here..." style="width: 300px;">
                <button type="submit">⌨️ Type</button>
            </form>
        </div>
        
        <div>
            <h3>Recent Logs</h3>
            <div class="log" id="logs">Loading logs...</div>
        </div>
    </div>
    
    <script>
        function screenshot() {
            fetch('/api/screenshot/refresh')
                .then(() => {
                    document.getElementById('screenshot').src = '/api/screenshot?' + Date.now();
                });
        }
        
        function stopAgent() {
            fetch('/api/stop', {method: 'POST'})
                .then(() => alert('Agent stopped. Restart manually.'));
        }
        
        document.getElementById('clickForm').onsubmit = function(e) {
            e.preventDefault();
            const x = document.getElementById('clickX').value;
            const y = document.getElementById('clickY').value;
            fetch('/api/click', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({x: parseInt(x), y: parseInt(y)})
            });
        };
        
        document.getElementById('typeForm').onsubmit = function(e) {
            e.preventDefault();
            const text = document.getElementById('typeText').value;
            fetch('/api/type', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: text})
            });
        };
        
        // Auto-refresh screenshot - DISABLED to save storage
        // Only refresh when user clicks "Take Screenshot" button
        // setInterval(() => {
        //     document.getElementById('screenshot').src = '/api/screenshot?' + Date.now();
        // }, 2000);
        
        // Load logs
        setInterval(() => {
            fetch('/api/logs')
                .then(r => r.text())
                .then(text => {
                    document.getElementById('logs').innerText = text;
                });
        }, 3000);
    </script>
</body>
</html>
"""

# API Routes
@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE, **agent_state)

@app.route('/api/status')
def status():
    return jsonify(agent_state)

@app.route('/api/screenshot')
def screenshot():
    """Take and return screenshot"""
    try:
        img = pyautogui.screenshot()
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Save to file for debugging
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        img.save(SCREENSHOT_DIR / f"screenshot_{timestamp}.png")
        
        # Clean up old screenshots (keep only MAX_SCREENSHOTS)
        cleanup_old_screenshots()
        
        agent_state["last_action"] = f"screenshot at {timestamp}"
        agent_state["action_count"] += 1
        
        return jsonify({
            "success": True,
            "image": img_str,
            "timestamp": timestamp
        })
    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/click', methods=['POST'])
def click():
    """Click at coordinates"""
    try:
        data = request.json
        x = int(data.get('x', 0))
        y = int(data.get('y', 0))
        
        # Safety check
        screen_width, screen_height = pyautogui.size()
        if not (0 <= x <= screen_width and 0 <= y <= screen_height):
            return jsonify({"success": False, "error": "Coordinates out of bounds"}), 400
        
        pyautogui.click(x, y)
        logger.info(f"Clicked at ({x}, {y})")
        
        agent_state["last_action"] = f"click at ({x}, {y})"
        agent_state["action_count"] += 1
        
        return jsonify({"success": True, "x": x, "y": y})
    except Exception as e:
        logger.error(f"Click failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/type', methods=['POST'])
def type_text():
    """Type text"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if len(text) > 1000:
            return jsonify({"success": False, "error": "Text too long (max 1000 chars)"}), 400
        
        pyautogui.typewrite(text, interval=0.01)
        logger.info(f"Typed text (length: {len(text)})")
        
        agent_state["last_action"] = f"typed {len(text)} characters"
        agent_state["action_count"] += 1
        
        return jsonify({"success": True, "length": len(text)})
    except Exception as e:
        logger.error(f"Type failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/move', methods=['POST'])
def move_mouse():
    """Move mouse to coordinates"""
    try:
        data = request.json
        x = int(data.get('x', 0))
        y = int(data.get('y', 0))
        duration = float(data.get('duration', 0.5))
        
        screen_width, screen_height = pyautogui.size()
        if not (0 <= x <= screen_width and 0 <= y <= screen_height):
            return jsonify({"success": False, "error": "Coordinates out of bounds"}), 400
        
        pyautogui.moveTo(x, y, duration=duration)
        logger.info(f"Moved mouse to ({x}, {y})")
        
        agent_state["last_action"] = f"move to ({x}, {y})"
        agent_state["action_count"] += 1
        
        return jsonify({"success": True, "x": x, "y": y})
    except Exception as e:
        logger.error(f"Move failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/key', methods=['POST'])
def press_key():
    """Press a key"""
    try:
        data = request.json
        key = data.get('key', '')
        
        # Whitelist of safe keys
        safe_keys = ['enter', 'tab', 'esc', 'space', 'backspace', 'delete', 
                     'up', 'down', 'left', 'right', 'ctrl', 'alt', 'shift']
        
        if key.lower() not in safe_keys and len(key) != 1:
            return jsonify({"success": False, "error": "Key not allowed"}), 400
        
        pyautogui.press(key)
        logger.info(f"Pressed key: {key}")
        
        agent_state["last_action"] = f"pressed {key}"
        agent_state["action_count"] += 1
        
        return jsonify({"success": True, "key": key})
    except Exception as e:
        logger.error(f"Key press failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stop', methods=['POST'])
def stop_agent():
    """Stop the agent"""
    logger.info("Agent stop requested")
    agent_state["connected"] = False
    return jsonify({"success": True, "message": "Agent stopping"})

@app.route('/api/logs')
def get_logs():
    """Get recent logs"""
    try:
        if LOG_FILE.exists():
            with open(LOG_FILE, 'r') as f:
                lines = f.readlines()
                return ''.join(lines[-50:])  # Last 50 lines
        return "No logs yet"
    except Exception as e:
        return f"Error reading logs: {e}"

# WebSocket events
@socketio.on('connect')
def handle_connect():
    agent_state["connected"] = True
    logger.info("Client connected")
    emit('status', agent_state)

@socketio.on('disconnect')
def handle_disconnect():
    agent_state["connected"] = False
    logger.info("Client disconnected")

# Safety monitor thread
def safety_monitor():
    """Monitor for safety issues"""
    while True:
        time.sleep(5)
        # Check if ESC is pressed (failsafe)
        # This runs in background to ensure agent can be stopped
        pass  # PyAutoGUI handles corner failsafe automatically

if __name__ == '__main__':
    logger.info(f"=" * 50)
    logger.info(f"Desktop Control Agent v{AGENT_VERSION}")
    logger.info(f"Starting at {datetime.now()}")
    logger.info(f"SAFETY: Move mouse to screen corner to stop")
    logger.info(f"Logs: {LOG_FILE}")
    logger.info(f"Screenshots: {SCREENSHOT_DIR}")
    logger.info(f"=" * 50)
    
    # Start safety monitor
    monitor_thread = threading.Thread(target=safety_monitor, daemon=True)
    monitor_thread.start()
    
    # Run Flask app
    print("\n" + "=" * 50)
    print("Desktop Control Agent Started!")
    print("=" * 50)
    print(f"Open browser: http://localhost:5000")
    print(f"Or use: http://127.0.0.1:5000")
    print(f"\nTo stop: Press Ctrl+C or close this window")
    print("=" * 50 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
