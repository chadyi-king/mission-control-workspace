# Tool Bridge Setup Guide for Chad
## From CHAD_YI (OpenClaw) - Complete Step-by-Step

---

## What This Is

The **Tool Bridge** is a REST API server that lets agents (like Kimi-Claw-Helios) access tools on your local machine:
- Execute shell commands
- Read/write files in the workspace
- Generate images via OpenAI

It runs as a background service on port 9001.

---

## Prerequisites

Before starting, make sure you have:
- [ ] Python 3.8+ installed
- [ ] pip (Python package manager)
- [ ] Git installed
- [ ] GitHub account (you have this ✅)
- [ ] Admin/sudo access to your machine

---

## Step 1: Clone the Repository

Open your terminal/command prompt and run:

```bash
# Navigate to where you want the project (e.g., home directory)
cd ~

# Clone the repository
git clone https://github.com/chadyi-king/openclaw-workspace.git

# Enter the directory
cd openclaw-workspace

# Check what you have
ls -la
```

You should see folders like:
- `agents/`
- `infrastructure/`
- `mission-control-dashboard/`
- `skills/`

---

## Step 2: Install Python Dependencies

The tool bridge uses Flask (a Python web framework). Install it:

```bash
# Make sure you're in the openclaw-workspace directory
cd ~/openclaw-workspace

# Install Flask
pip install flask

# Or if you prefer to use a requirements file (if one exists):
# pip install -r requirements.txt
```

**Verify Flask is installed:**
```bash
python3 -c "import flask; print('Flask OK:', flask.__version__)"
```

---

## Step 3: Configure API Keys

The tool bridge needs an API keys file. Create it:

```bash
# Navigate to the tool-bridge directory
cd ~/openclaw-workspace/infrastructure/tool-bridge

# Create the api-keys.json file
cat > api-keys.json << 'EOF'
{
  "openai": null,
  "allowed_agents": [
    "forger",
    "helios", 
    "escritor",
    "quanta",
    "mensamusa",
    "autour",
    "chad_yi",
    "kimi-claw-helios"
  ]
}
EOF
```

**Optional - Add OpenAI API key** (if you want image generation):
```bash
# Edit the file and add your key
nano api-keys.json
```

Change `"openai": null` to `"openai": "your-key-here"`

---

## Step 4: Test the Server (Manual Run)

Before setting up the service, test that it works:

```bash
# Make sure you're in the tool-bridge directory
cd ~/openclaw-workspace/infrastructure/tool-bridge

# Run the server
python3 server.py
```

You should see:
```
==================================================
Tool Bridge Service Starting...
REST API on http://localhost:9001
==================================================
 * Running on http://localhost:9001
```

**Test it's working** (open a new terminal):
```bash
# Health check
curl http://localhost:9001/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-...",
  "tools_available": ["exec", "file_write", "file_read", "image_gen"]
}
```

**Stop the test server** (Ctrl+C in the first terminal).

---

## Step 5: Set Up as a System Service (Linux/Mac)

### For Linux (systemd):

```bash
# Copy the service file to systemd
sudo cp ~/openclaw-workspace/infrastructure/tool-bridge/tool-bridge.service /etc/systemd/system/

# Edit it to match your username
sudo nano /etc/systemd/system/tool-bridge.service
```

**Change these lines to match your system:**
```ini
WorkingDirectory=/home/YOUR_USERNAME/openclaw-workspace
ExecStart=/usr/bin/python3 /home/YOUR_USERNAME/openclaw-workspace/infrastructure/tool-bridge/server.py
Environment=PYTHONPATH=/home/YOUR_USERNAME/openclaw-workspace
```

Replace `YOUR_USERNAME` with your actual username (e.g., `chad`).

**Enable and start the service:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable the service (starts on boot)
sudo systemctl enable tool-bridge

# Start the service now
sudo systemctl start tool-bridge

# Check status
sudo systemctl status tool-bridge
```

You should see "active (running)" in green.

---

### For Mac (launchd):

Create a launch agent:

```bash
# Create the plist file
cat > ~/Library/LaunchAgents/com.openclaw.tool-bridge.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.tool-bridge</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/YOUR_USERNAME/openclaw-workspace/infrastructure/tool-bridge/server.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/YOUR_USERNAME/openclaw-workspace</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/tool-bridge.out</string>
    <key>StandardErrorPath</key>
    <string>/tmp/tool-bridge.err</string>
</dict>
</plist>
EOF
```

Replace `YOUR_USERNAME` with your Mac username.

**Load and start:**
```bash
launchctl load ~/Library/LaunchAgents/com.openclaw.tool-bridge.plist
launchctl start com.openclaw.tool-bridge
```

---

### For Windows:

Windows setup is different. You'll need to:
1. Use Task Scheduler, OR
2. Run manually in a background terminal

**Simple approach - Batch file:**
Create `start-bridge.bat`:
```batch
@echo off
cd C:\Users\YOUR_USERNAME\openclaw-workspace\infrastructure\tool-bridge
python server.py
```

Double-click to run, or add to startup folder.

---

## Step 6: Test the Service

Once the service is running:

```bash
# Health check
curl http://localhost:9001/health

# Test file write
curl -X POST http://localhost:9001/file/write \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "chad_yi",
    "path": "test/hello.txt",
    "content": "Hello from Tool Bridge!"
  }'

# Test file read
curl -X POST http://localhost:9001/file/read \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "chad_yi",
    "path": "test/hello.txt"
  }'
```

---

## Step 7: Configure Kimi-Claw-Helios

Now tell Kimi-Claw-Helios about the bridge:

Add to Kimi Claw's memory:
```
TOOL_BRIDGE_URL=http://localhost:9001

Available endpoints:
- GET  /health - Check if bridge is alive
- POST /exec - Run shell commands
- POST /file/write - Write files
- POST /file/read - Read files
- POST /image/gen - Generate images

Required in all POST requests:
- agent_id: your agent name
```

---

## Troubleshooting

### "Port 9001 already in use"
```bash
# Find what's using it
lsof -i :9001

# Kill it
kill -9 <PID>

# Or use a different port in server.py
```

### "Permission denied"
```bash
# Fix permissions
chmod +x ~/openclaw-workspace/infrastructure/tool-bridge/server.py
```

### "Module not found: flask"
```bash
# Install flask properly
pip3 install flask

# Or use python3 explicitly
python3 -m pip install flask
```

### Service won't start (Linux)
```bash
# Check logs
sudo journalctl -u tool-bridge -f

# Check for syntax errors
python3 ~/openclaw-workspace/infrastructure/tool-bridge/server.py
```

---

## Quick Commands Reference

```bash
# Check if bridge is running
curl http://localhost:9001/health

# View service logs (Linux)
sudo journalctl -u tool-bridge -f

# Restart service (Linux)
sudo systemctl restart tool-bridge

# Stop service (Linux)
sudo systemctl stop tool-bridge

# Disable auto-start (Linux)
sudo systemctl disable tool-bridge
```

---

## What Happens Next

1. **You**: Set up the tool bridge on your machine (follow this guide)
2. **Kimi-Claw-Helios**: Connects to `http://your-ip:9001` to use tools
3. **CHAD_YI**: Can now delegate file operations and commands to Kimi
4. **Result**: Full agent integration with Mission Control

---

## Security Notes

⚠️ **Important:**
- The bridge only accepts requests from `allowed_agents` list
- File operations are restricted to the workspace directory
- Dangerous commands (rm -rf /, etc.) are blocked
- Don't expose port 9001 to the internet (localhost only)

---

## Need Help?

If something breaks:
1. Check the service logs (`journalctl -u tool-bridge -f`)
2. Test manually (`python3 server.py`)
3. Message CHAD_YI with the error

---

**Created by**: CHAD_YI  
**Last Updated**: 2026-02-17  
**Version**: 1.0
