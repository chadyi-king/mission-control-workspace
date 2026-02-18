#!/usr/bin/env python3
"""
Redis Bridge - Check for messages from Helios
Connects to Upstash Redis and polls for messages
"""
import sys
import time
import json
sys.path.insert(0, '/home/chad-yi/.openclaw/workspace')

from sync.redis_comm import RedisComm

def main():
    results = []
    messages_received = []
    
    # Initialize as "chad" 
    comm = RedisComm(node_name="chad")
    
    # Register handlers to capture messages
    def on_task(data):
        messages_received.append({"type": "task", "data": data})
        # Reply with ack
        comm.send("helios", "ack", {
            "received": True,
            "task_id": data.get('data', {}).get('id'),
            "timestamp": time.time()
        })
    
    def on_test(data):
        messages_received.append({"type": "test", "data": data})
        # Reply to test
        comm.send("helios", "test_reply", {
            "message": "Hello Helios! Chad here. Redis bridge working.",
            "timestamp": time.time()
        })
    
    def on_message(data):
        messages_received.append({"type": "message", "data": data})
        # Generic reply
        comm.send("helios", "ack", {
            "received": True,
            "original_type": data.get('type'),
            "timestamp": time.time()
        })
    
    def on_ping(data):
        messages_received.append({"type": "ping", "data": data})
        # Pong back
        comm.send("helios", "pong", {
            "timestamp": time.time()
        })
    
    # Register all handlers
    comm.on("task", on_task)
    comm.on("test", on_test)
    comm.on("message", on_message)
    comm.on("ping", on_ping)
    
    # Start listening
    comm.start_listening(["helios", "broadcast"])
    
    # Listen for 5 seconds to catch any messages
    time.sleep(5)
    
    # Stop listening
    comm.stop()
    
    # Report results
    if messages_received:
        print("=" * 50)
        print("📨 MESSAGES FROM HELIOS")
        print("=" * 50)
        for msg in messages_received:
            data = msg['data']
            print(f"\n🔹 Type: {msg['type'].upper()}")
            print(f"   From: {data.get('from', 'unknown')}")
            print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
            print(f"   Data: {json.dumps(data.get('data', {}), indent=2)}")
        print(f"\n✅ Replied to all {len(messages_received)} message(s)")
        print("=" * 50)
        return True
    else:
        # No messages - stay silent per instructions
        return False

if __name__ == "__main__":
    found = main()
    sys.exit(0 if found else 0)
