#!/usr/bin/env python3
"""
Chad Auto-Responder - Run this on Chad's machine
"""

import json
import time
import os
import sys
from datetime import datetime

# Install redis if needed: pip install redis
import redis

class ChadAutoResponder:
    def __init__(self):
        self.node_name = "chad"
        # Connect to Upstash Redis
        self.redis = redis.Redis(
            host='national-gar-36005.upstash.io',
            port=6379,
            password='AYylAAIncDJkMDBlNjYyOGNjZWM0NDk4ODJlODgxOTVjZjllNzc2N3AyMzYwMDU',
            username='default',
            ssl=True,
            decode_responses=True
        )
        self.pubsub = None
        self.running = False
        
    def send_to_helios(self, msg_type: str, data: dict):
        """Send message to Helios"""
        message = {
            "from": self.node_name,
            "type": msg_type,
            "timestamp": time.time(),
            "data": data
        }
        # Channel: chad→helios
        self.redis.publish(f"chad\u2192helios", json.dumps(message))
        print(f"[CHAD] → Helios: {msg_type}")
    
    def handle_helios_message(self, message):
        """Auto-handle messages from Helios"""
        try:
            data = json.loads(message['data'])
        except:
            return
            
        msg_type = data.get('type', 'unknown')
        payload = data.get('data', {})
        from_node = data.get('from', 'unknown')
        
        print(f"[CHAD] ← {from_node}: {msg_type}")
        
        # AUTO-RESPONSES - This is the key part!
        if msg_type == "pong":
            print(f"[CHAD] Helios is alive, responding...")
            # Auto-reply with status
            self.send_to_helios("status", {
                "agent": "chad",
                "status": "active",
                "tasks": 3
            })
            
        elif msg_type == "task":
            task = payload
            print(f"[CHAD] Received task: {task.get('message', 'No details')}")
            # Acknowledge
            self.send_to_helios("ack", {
                "task_id": task.get('id'),
                "status": "accepted"
            })
            # Process task (would spawn agent here)
            print(f"[CHAD] Processing task...")
            time.sleep(2)  # Simulate work
            self.send_to_helios("task_complete", {
                "task_id": task.get('id'),
                "result": "success"
            })
            
        elif msg_type == "status_response":
            print(f"[CHAD] Helios status: {payload}")
            
        elif msg_type == "alert":
            print(f"[CHAD] ALERT from Helios: {payload.get('message', '')}")
            # Could trigger notification
            
        else:
            # Echo back for any unknown message
            print(f"[CHAD] Echoing back...")
            self.send_to_helios("echo", {
                "received": msg_type,
                "original": payload
            })
    
    def start(self):
        """Start listening - THIS RUNS FOREVER"""
        self.running = True
        
        print("="*60)
        print("🚀 CHAD AUTO-RESPONDER")
        print("="*60)
        print("[CHAD] Connecting to Redis...")
        
        self.pubsub = self.redis.pubsub()
        # Subscribe to helios→chad channel
        self.pubsub.subscribe('helios→chad')
        
        print("[CHAD] ✅ Listening for Helios messages...")
        print("[CHAD] Press Ctrl+C to stop")
        print("-"*60)
        
        # Send initial ping
        self.send_to_helios("ping", {"startup": True})
        
        # Listen loop - THIS IS THE MAGIC
        try:
            for message in self.pubsub.listen():
                if not self.running:
                    break
                if message['type'] == 'message':
                    self.handle_helios_message(message)
        except KeyboardInterrupt:
            print("\n[CHAD] Stopping...")
        finally:
            self.stop()
    
    def stop(self):
        self.running = False
        if self.pubsub:
            self.pubsub.unsubscribe()
        print("[CHAD] Stopped")

if __name__ == "__main__":
    responder = ChadAutoResponder()
    responder.start()
