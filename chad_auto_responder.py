#!/usr/bin/env python3
"""
Chad Auto-Responder Bridge
This runs on Chad's local machine, connects to same Redis, auto-responds to Helios
"""

import json
import time
import os
import sys
from datetime import datetime

# Chad needs to install redis: pip install redis
import redis

class ChadAutoResponder:
    """
    Runs on Chad's machine, auto-communicates with Helios
    """
    
    def __init__(self):
        self.node_name = "chad"
        # Chad needs to set this env var
        redis_url = os.environ.get('UPSTASH_REDIS_URL')
        if not redis_url:
            raise ValueError("UPSTASH_REDIS_URL not set")
        
        self.redis = redis.from_url(redis_url)
        self.pubsub = self.redis.pubsub()
        self.running = False
        
    def send_to_helios(self, msg_type: str, data: dict):
        """Send message to Helios"""
        message = {
            "from": self.node_name,
            "type": msg_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.redis.publish('helios', json.dumps(message))
        print(f"[CHAD] → Helios: {msg_type}")
    
    def handle_helios_message(self, message: dict):
        """Auto-handle messages from Helios"""
        data = json.loads(message['data'])
        msg_type = data.get('type', 'unknown')
        payload = data.get('data', {})
        
        print(f"[CHAD] ← Helios: {msg_type}")
        
        # Auto-responses
        if msg_type == "task_assigned":
            task = payload.get('task', {})
            print(f"[CHAD] Task assigned: {task.get('title', 'Untitled')}")
            # Auto-acknowledge
            self.send_to_helios("task_ack", {
                "task_id": task.get('id'),
                "status": "accepted"
            })
            
        elif msg_type == "status_response":
            print(f"[CHAD] Status: {json.dumps(payload, indent=2)}")
            
        elif msg_type == "pong":
            print(f"[CHAD] Helios is alive")
            
        elif msg_type == "alert":
            alert = payload
            print(f"[CHAD] ALERT: {alert.get('message', '')}")
            # Could trigger local notification here
            
        elif msg_type == "spawn_agent":
            agent_id = payload.get('agent_id')
            print(f"[CHAD] Spawning agent: {agent_id}")
            # Auto-respond
            self.send_to_helios("agent_spawned", {
                "agent_id": agent_id,
                "status": "spawning"
            })
            
        else:
            print(f"[CHAD] Unknown message type: {msg_type}")
    
    def start(self):
        """Start listening"""
        self.running = True
        
        print("[CHAD] Auto-Responder starting...")
        print("[CHAD] Subscribing to helios channel...")
        
        self.pubsub.subscribe('chad')
        
        print("[CHAD] Listening...")
        
        try:
            for message in self.pubsub.listen():
                if message['type'] == 'message':
                    self.handle_helios_message(message)
                    
        except KeyboardInterrupt:
            print("\n[CHAD] Stopping...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop listening"""
        self.running = False
        self.pubsub.unsubscribe()
        print("[CHAD] Stopped")

if __name__ == "__main__":
    responder = ChadAutoResponder()
    responder.start()
