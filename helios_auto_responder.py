#!/usr/bin/env python3
"""
Auto-Responder Bridge for Helios
Runs continuously, listens for Redis messages, auto-triggers responses
"""

import json
import time
import os
import sys
from datetime import datetime
from pathlib import Path

# Add sync module to path
sys.path.insert(0, '/root/.openclaw/workspace/mission-control-workspace')
from sync.redis_comm import RedisComm

class HeliosAutoResponder:
    """
    Continuous listener that:
    1. Subscribes to Redis channels
    2. Receives messages from Chad/other agents
    3. Auto-generates responses without human intervention
    """
    
    def __init__(self):
        self.node_name = "helios"
        self.comm = RedisComm(node_name=self.node_name)
        self.running = False
        self.message_log = "/root/.openclaw/workspace/mission-control-workspace/logs/helios_messages.jsonl"
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.message_log), exist_ok=True)
        
        # Register handlers
        self.comm.on("task", self.handle_task)
        self.comm.on("ack", self.handle_ack)
        self.comm.on("ping", self.handle_ping)
        self.comm.on("status_request", self.handle_status_request)
        self.comm.on("spawn_request", self.handle_spawn_request)
        self.comm.on("message", self.handle_generic_message)
        
    def log_message(self, msg_type: str, data: dict):
        """Log all messages for audit trail"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": msg_type,
            "data": data
        }
        with open(self.message_log, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def handle_task(self, data: dict):
        """Handle incoming task from Chad"""
        from_node = data.get('from', 'unknown')
        task = data.get('data', {})
        
        print(f"[AUTO-RESPONDER] Task from {from_node}: {task.get('message', 'No message')}")
        self.log_message("task_received", data)
        
        # Auto-acknowledge
        self.comm.send(from_node, "ack", {
            "task_id": task.get('id', 'unknown'),
            "status": "received_by_helios",
            "timestamp": datetime.now().isoformat()
        })
        
        # Auto-route to appropriate agent
        self.route_task(task)
    
    def handle_ack(self, data: dict):
        """Handle acknowledgment"""
        from_node = data.get('from', 'unknown')
        ack_data = data.get('data', {})
        print(f"[AUTO-RESPONDER] Ack from {from_node}: {ack_data}")
        self.log_message("ack_received", data)
    
    def handle_ping(self, data: dict):
        """Auto-respond to pings"""
        from_node = data.get('from', 'unknown')
        print(f"[AUTO-RESPONDER] Ping from {from_node}")
        
        # Auto-pong
        self.comm.send(from_node, "pong", {
            "from": "helios",
            "status": "active",
            "timestamp": datetime.now().isoformat()
        })
        self.log_message("ping_pong", data)
    
    def handle_status_request(self, data: dict):
        """Auto-send status"""
        from_node = data.get('from', 'unknown')
        print(f"[AUTO-RESPONDER] Status request from {from_node}")
        
        status = self.get_system_status()
        self.comm.send(from_node, "status_response", status)
        self.log_message("status_sent", {"to": from_node, "status": status})
    
    def handle_spawn_request(self, data: dict):
        """Handle agent spawn request"""
        from_node = data.get('from', 'unknown')
        payload = data.get('data', {})
        agent_id = payload.get('agent_id', 'unknown')
        
        print(f"[AUTO-RESPONDER] Spawn request from {from_node}: {agent_id}")
        
        # Update dashboard
        self.update_agent_status(agent_id, "spawning", payload.get('config', {}))
        
        # Broadcast spawn
        self.comm.broadcast("spawn_agent", {
            "agent_id": agent_id,
            "config": payload.get('config', {}),
            "requested_by": from_node,
            "timestamp": datetime.now().isoformat()
        })
        
        # Acknowledge
        self.comm.send(from_node, "ack", {
            "spawn_request": agent_id,
            "status": "broadcasted"
        })
        
        self.log_message("spawn_broadcasted", data)
    
    def handle_generic_message(self, data: dict):
        """Handle generic messages"""
        from_node = data.get('from', 'unknown')
        msg = data.get('data', {}).get('message', '')
        print(f"[AUTO-RESPONDER] Message from {from_node}: {msg}")
        self.log_message("generic_message", data)
    
    def route_task(self, task: dict):
        """Auto-route task to appropriate agent"""
        task_type = task.get('type', 'general')
        
        routing = {
            'writing': 'escritor',
            'trading': 'quanta', 
            'monitoring': 'mensamusa',
            'scripting': 'autour',
            'design': 'forger',
            'audit': 'helios'
        }
        
        target = routing.get(task_type, 'chad')
        
        # Send to agent via Redis
        self.comm.send(target, "task", {
            "original_task": task,
            "routed_by": "helios",
            "routed_at": datetime.now().isoformat()
        })
        
        print(f"[AUTO-RESPONDER] Routed task to {target}")
    
    def get_system_status(self) -> dict:
        """Get current system status from dashboard"""
        try:
            with open("/root/.openclaw/workspace/mission-control-workspace/data.json", 'r') as f:
                return json.load(f)
        except:
            return {"error": "Could not load dashboard"}
    
    def update_agent_status(self, agent_id: str, status: str, info: dict = None):
        """Update agent status in dashboard"""
        try:
            data = self.get_system_status()
            
            if 'agents' not in data:
                data['agents'] = {}
            
            data['agents'][agent_id] = {
                **(info or {}),
                "status": status,
                "last_updated": datetime.now().isoformat()
            }
            data['lastUpdated'] = datetime.now().isoformat()
            
            with open("/root/.openclaw/workspace/mission-control-workspace/data.json", 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[AUTO-RESPONDER] Error updating dashboard: {e}")
    
    def start(self):
        """Start the auto-responder"""
        self.running = True
        
        print("=" * 60)
        print("🚀 HELIOS AUTO-RESPONDER")
        print("=" * 60)
        print("[AUTO-RESPONDER] Starting...")
        print("[AUTO-RESPONDER] Connecting to Redis...")
        
        # Subscribe to channels
        self.comm.start_listening(["chad", "broadcast"])
        
        print("[AUTO-RESPONDER] ✅ Listening for messages...")
        print("[AUTO-RESPONDER] Press Ctrl+C to stop")
        print("-" * 60)
        
        # Send startup ping
        self.comm.broadcast("message", {
            "text": "Helios Auto-Responder started",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[AUTO-RESPONDER] Stopping...")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the auto-responder"""
        self.running = False
        self.comm.stop()
        print("[AUTO-RESPONDER] Stopped")


if __name__ == "__main__":
    responder = HeliosAutoResponder()
    responder.start()
