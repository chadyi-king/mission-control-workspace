#!/usr/bin/env python3
"""
Helios Background Worker for Render.com
This runs continuously as a Background Worker service
"""

import json
import time
import os
import sys
from datetime import datetime

# Add sync module to path
sys.path.insert(0, '/app')
from sync.redis_comm import RedisComm

class HeliosBackgroundWorker:
    """
    Continuous background worker that:
    - Listens to Redis 24/7
    - Auto-responds to messages
    - Executes tasks
    - Reports status
    """
    
    def __init__(self):
        self.node_name = "helios"
        self.comm = RedisComm(node_name=self.node_name)
        self.running = False
        
        # Register message handlers
        self.comm.on("ping", self.handle_ping)
        self.comm.on("task", self.handle_task)
        self.comm.on("status_request", self.handle_status_request)
        self.comm.on("message", self.handle_message)
        self.comm.on("command", self.handle_command)
        
    def log(self, msg: str):
        """Log with timestamp"""
        print(f"[{datetime.now().isoformat()}] {msg}", flush=True)
    
    def handle_ping(self, data: dict):
        """Respond to pings"""
        from_node = data.get('from', 'unknown')
        self.log(f"Ping from {from_node}")
        self.comm.send(from_node, "pong", {
            "status": "alive",
            "timestamp": datetime.now().isoformat()
        })
    
    def handle_task(self, data: dict):
        """Execute tasks"""
        from_node = data.get('from', 'unknown')
        task = data.get('data', {})
        task_id = task.get('id', 'unknown')
        
        self.log(f"Task from {from_node}: {task_id}")
        
        # Execute based on task type
        task_type = task.get('type', 'generic')
        result = {"status": "completed"}
        
        if task_type == 'audit':
            # Run audit
            try:
                with open('/app/data.json', 'r') as f:
                    dashboard = json.load(f)
                result['data'] = dashboard
            except Exception as e:
                result = {"status": "error", "error": str(e)}
                
        elif task_type == 'update':
            # Update dashboard
            try:
                with open('/app/data.json', 'r') as f:
                    dashboard = json.load(f)
                dashboard['lastUpdated'] = datetime.now().isoformat()
                with open('/app/data.json', 'w') as f:
                    json.dump(dashboard, f, indent=2)
                result['message'] = 'Dashboard updated'
            except Exception as e:
                result = {"status": "error", "error": str(e)}
        
        # Send result back
        self.comm.send(from_node, "task_complete", {
            "task_id": task_id,
            "result": result
        })
        self.log(f"Task {task_id} completed")
    
    def handle_status_request(self, data: dict):
        """Send status"""
        from_node = data.get('from', 'unknown')
        self.log(f"Status request from {from_node}")
        
        try:
            with open('/app/data.json', 'r') as f:
                status = json.load(f)
        except:
            status = {"error": "Could not load status"}
        
        self.comm.send(from_node, "status_response", status)
    
    def handle_message(self, data: dict):
        """Handle generic messages"""
        from_node = data.get('from', 'unknown')
        text = data.get('data', {}).get('text', '')
        self.log(f"Message from {from_node}: {text}")
        
        # Echo back
        self.comm.send(from_node, "message", {
            "text": f"Helios received: {text}",
            "echo": True
        })
    
    def handle_command(self, data: dict):
        """Execute commands"""
        from_node = data.get('from', 'unknown')
        cmd = data.get('data', {}).get('command', '')
        self.log(f"Command from {from_node}: {cmd}")
        
        # For security, only allow safe commands
        allowed_prefixes = ['cat ', 'ls ', 'pwd', 'echo ', 'python3 ']
        is_allowed = any(cmd.startswith(p) for p in allowed_prefixes)
        
        if is_allowed:
            import subprocess
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                output = result.stdout if result.returncode == 0 else result.stderr
            except Exception as e:
                output = str(e)
        else:
            output = "Command not allowed for security"
        
        self.comm.send(from_node, "command_result", {
            "command": cmd,
            "output": output
        })
    
    def heartbeat(self):
        """Send periodic heartbeat"""
        while self.running:
            self.comm.broadcast("heartbeat", {
                "from": self.node_name,
                "status": "active",
                "timestamp": datetime.now().isoformat()
            })
            time.sleep(30)  # Every 30 seconds
    
    def start(self):
        """Start the background worker"""
        self.running = True
        
        self.log("=" * 60)
        self.log("🚀 HELIOS BACKGROUND WORKER STARTED")
        self.log("=" * 60)
        self.log("Listening for messages...")
        
        # Start listening
        self.comm.start_listening(["chad", "broadcast"])
        
        # Start heartbeat in background thread
        import threading
        hb_thread = threading.Thread(target=self.heartbeat, daemon=True)
        hb_thread.start()
        
        # Announce startup
        self.comm.broadcast("message", {
            "text": "Helios Background Worker started on Render",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep running forever
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.log("Shutting down...")
        finally:
            self.stop()
    
    def stop(self):
        self.running = False
        self.comm.stop()
        self.log("Stopped")

if __name__ == "__main__":
    worker = HeliosBackgroundWorker()
    worker.start()
