#!/usr/bin/env python3
"""
Redis LOW Channel Checker - Silent Archive
Checks Helios LOW priority channel every 30 minutes, archives silently.
Never reports to user.
"""

import sys
import json
import time
import os
from datetime import datetime

sys.path.insert(0, '/home/chad-yi/.openclaw/workspace')
from sync.redis_comm import RedisComm

# Archive file path (daily rotation)
today = datetime.now().strftime('%Y-%m-%d')
ARCHIVE_DIR = '/home/chad-yi/.openclaw/workspace/archive/redis_low'
ARCHIVE_FILE = f"{ARCHIVE_DIR}/helios_low_{today}.jsonl"

# Ensure archive directory exists
os.makedirs(ARCHIVE_DIR, exist_ok=True)

# Collect messages
messages_received = []

def on_low_priority(data):
    """Handle LOW priority messages from Helios"""
    messages_received.append({
        "archived_at": time.time(),
        "type": data.get("type"),
        "from": data.get("from"),
        "priority": data.get("priority", "low"),
        "data": data.get("data"),
        "timestamp": data.get("timestamp")
    })

def on_heartbeat(data):
    """Handle heartbeat messages"""
    messages_received.append({
        "archived_at": time.time(),
        "type": "heartbeat",
        "from": data.get("from"),
        "priority": "low",
        "data": data.get("data"),
        "timestamp": data.get("timestamp")
    })

def on_log(data):
    """Handle log messages"""
    messages_received.append({
        "archived_at": time.time(),
        "type": "log",
        "from": data.get("from"),
        "priority": "low",
        "data": data.get("data"),
        "timestamp": data.get("timestamp")
    })

# Initialize as chad node
comm = RedisComm(node_name="chad")

# Register handlers for LOW priority messages
comm.on("low", on_low_priority)
comm.on("heartbeat", on_heartbeat)
comm.on("log", on_log)
comm.on("status", on_log)  # Status reports treated as low priority

# Listen on helios→chad and broadcast channels
comm.start_listening(["helios", "broadcast"])

# Listen for 5 seconds to collect messages
time.sleep(5)

# Stop listening
comm.stop()

# Archive messages silently (no output to user)
if messages_received:
    with open(ARCHIVE_FILE, 'a') as f:
        for msg in messages_received:
            f.write(json.dumps(msg) + '\n')

# Exit silently - no output to user
sys.exit(0)
