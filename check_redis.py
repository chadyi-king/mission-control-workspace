#!/usr/bin/env python3
"""
Redis Bridge Checker - Poll for messages from Helios
"""

import sys
import json
import time
sys.path.insert(0, '/home/chad-yi/.openclaw/workspace')

from sync.redis_comm import RedisComm

# Track messages received
messages_received = []
reply_status = []

def on_task(data):
    """Handle task messages from Helios"""
    messages_received.append({
        "type": "task",
        "from": data.get("from"),
        "data": data.get("data"),
        "timestamp": data.get("timestamp")
    })
    # Send acknowledgement
    success = comm.send(data["from"], "ack", {
        "task_id": data["data"].get("id") if data.get("data") else None,
        "status": "received",
        "by": "chad-yi",
        "time": time.time()
    })
    reply_status.append({"type": "ack", "to": data["from"], "success": success})

def on_ping(data):
    """Handle ping messages"""
    messages_received.append({
        "type": "ping", 
        "from": data.get("from"),
        "data": data.get("data"),
        "timestamp": data.get("timestamp")
    })
    # Send pong
    success = comm.send(data["from"], "pong", {"echo": data.get("data"), "time": time.time()})
    reply_status.append({"type": "pong", "to": data["from"], "success": success})

def on_message(data):
    """Handle generic messages"""
    messages_received.append({
        "type": data.get("type", "unknown"),
        "from": data.get("from"),
        "data": data.get("data"),
        "timestamp": data.get("timestamp")
    })
    # Acknowledge
    success = comm.send(data["from"], "ack", {"received": True, "original_type": data.get("type")})
    reply_status.append({"type": "ack", "to": data["from"], "success": success})

# Initialize as chad node
comm = RedisComm(node_name="chad")

# Register handlers
comm.on("task", on_task)
comm.on("ping", on_ping)
comm.on("message", on_message)
comm.on("test", on_message)

# Start listening for a short window
comm.start_listening(["helios", "broadcast"])

# Listen for 5 seconds
time.sleep(5)

# Stop listening
comm.stop()

# Report results
if messages_received:
    print("=" * 50)
    print("📨 MESSAGES RECEIVED FROM HELIOS")
    print("=" * 50)
    for i, msg in enumerate(messages_received, 1):
        print(f"\n[{i}] Type: {msg['type']}")
        print(f"    From: {msg['from']}")
        print(f"    Data: {json.dumps(msg['data'], indent=2) if msg['data'] else 'None'}")
        print(f"    Time: {msg['timestamp']}")
    
    print("\n" + "=" * 50)
    print("📤 REPLIES SENT")
    print("=" * 50)
    for reply in reply_status:
        status = "✅" if reply["success"] else "❌"
        print(f"{status} {reply['type'].upper()} → {reply['to']} (success={reply['success']})")
else:
    # No messages - stay silent as requested
    pass
