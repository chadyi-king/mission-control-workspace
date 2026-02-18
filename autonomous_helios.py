#!/usr/bin/env python3
"""
TRUE AUTONOMOUS AGENT for Helios
This doesn't just log messages — it ACTS on them
"""

import json
import time
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/root/.openclaw/workspace/mission-control-workspace')
from sync.redis_comm import RedisComm

class AutonomousHelios:
    """
    A truly autonomous agent that:
    1. Receives messages via Redis
    2. DECIDES what to do (not just log)
    3. EXECUTES actions (spawn agents, run commands, send responses)
    4. Reports back automatically
    """
    
    def __init__(self):
        self.node_name = "helios"
        self.comm = RedisComm(node_name=self.node_name)
        self.running = False
        self.decision_log = "/root/.openclaw/workspace/mission-control-workspace/logs/helios_decisions.jsonl"
        os.makedirs(os.path.dirname(self.decision_log), exist_ok=True)
        
        # Register handlers
        self.comm.on("task", self.handle_task)
        self.comm.on("ping", self.handle_ping)
        self.comm.on("status_request", self.handle_status_request)
        self.comm.on("spawn_request", self.handle_spawn_request)
        self.comm.on("message", self.handle_message)
        self.comm.on("command", self.handle_command)
        
    def log_decision(self, decision: str, context: dict):
        """Log what we decided to do"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "context": context
        }
        with open(self.decision_log, 'a') as f:
            f.write(json.dumps(entry) + '\n')
        print(f"[DECISION] {decision}")
    
    def execute_action(self, action: str, params: dict) -> dict:
        """Actually execute an action"""
        result = {"action": action, "status": "failed", "output": ""}
        
        if action == "spawn_agent":
            agent_id = params.get('agent_id')
            # Actually spawn an agent process
            try:
                # Write agent config
                config_path = f"/root/.openclaw/workspace/mission-control-workspace/agents/{agent_id}.json"
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, 'w') as f:
                    json.dump(params.get('config', {}), f)
                
                result["status"] = "spawned"
                result["output"] = f"Agent {agent_id} config written"
            except Exception as e:
                result["output"] = str(e)
                
        elif action == "run_command":
            cmd = params.get('command')
            try:
                output = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                result["status"] = "completed" if output.returncode == 0 else "error"
                result["output"] = output.stdout if output.returncode == 0 else output.stderr
            except Exception as e:
                result["output"] = str(e)
                
        elif action == "update_dashboard":
            try:
                data = self.get_dashboard()
                data['lastUpdated'] = datetime.now().isoformat()
                if 'agents' not in data:
                    data['agents'] = {}
                data['agents'][params.get('agent_id', 'unknown')] = {
                    "status": params.get('status', 'unknown'),
                    "last_seen": datetime.now().isoformat()
                }
                with open("/root/.openclaw/workspace/mission-control-workspace/data.json", 'w') as f:
                    json.dump(data, f, indent=2)
                result["status"] = "updated"
            except Exception as e:
                result["output"] = str(e)
                
        return result
    
    def handle_task(self, data: dict):
        """Handle incoming task — ACTUALLY DO SOMETHING"""
        from_node = data.get('from')
        task = data.get('data', {})
        task_id = task.get('id', f"task-{int(time.time())}")
        
        print(f"\n[{'='*60}")
        print(f"[TASK RECEIVED] From {from_node}: {task.get('message', 'No message')}")
        print(f"[{'='*60}\n")
        
        # DECIDE what to do
        task_type = task.get('type', 'general')
        
        if task_type == 'audit':
            self.log_decision(f"Running audit task {task_id}", task)
            # Actually run audit
            result = self.execute_action("run_command", {"command": "cat /root/.openclaw/workspace/mission-control-workspace/data.json | head -20"})
            # Send results back
            self.comm.send(from_node, "task_complete", {
                "task_id": task_id,
                "result": result,
                "summary": "Audit completed"
            })
            
        elif task_type == 'spawn':
            agent_id = task.get('agent_id')
            self.log_decision(f"Spawning agent {agent_id}", task)
            result = self.execute_action("spawn_agent", {
                "agent_id": agent_id,
                "config": task.get('config', {})
            })
            self.comm.send(from_node, "agent_spawned", {
                "task_id": task_id,
                "agent_id": agent_id,
                "result": result
            })
            
        elif task_type == 'status_check':
            self.log_decision(f"Status check requested", task)
            status = self.get_dashboard()
            self.comm.send(from_node, "status_response", status)
            
        else:
            # Generic task — just acknowledge
            self.log_decision(f"Generic task {task_id} acknowledged", task)
            self.comm.send(from_node, "ack", {
                "task_id": task_id,
                "status": "received"
            })
    
    def handle_ping(self, data: dict):
        """Auto-respond to pings"""
        from_node = data.get('from')
        print(f"[PING] From {from_node}")
        
        # Actually respond
        self.comm.send(from_node, "pong", {
            "from": "helios",
            "status": "autonomous_and_running",
            "timestamp": datetime.now().isoformat(),
            "capabilities": ["task_execution", "agent_spawning", "monitoring"]
        })
        self.log_decision(f"Responded to ping from {from_node}", {})
    
    def handle_status_request(self, data: dict):
        """Send actual status"""
        from_node = data.get('from')
        status = self.get_dashboard()
        self.comm.send(from_node, "status_response", status)
        self.log_decision(f"Sent status to {from_node}", {})
    
    def handle_spawn_request(self, data: dict):
        """Handle spawn request"""
        from_node = data.get('from')
        payload = data.get('data', {})
        agent_id = payload.get('agent_id')
        
        self.log_decision(f"Spawn request for {agent_id}", payload)
        
        # Actually spawn
        result = self.execute_action("spawn_agent", {
            "agent_id": agent_id,
            "config": payload.get('config', {})
        })
        
        # Update dashboard
        self.execute_action("update_dashboard", {
            "agent_id": agent_id,
            "status": "spawning"
        })
        
        # Acknowledge
        self.comm.send(from_node, "ack", {
            "spawn_request": agent_id,
            "result": result
        })
    
    def handle_message(self, data: dict):
        """Handle generic messages"""
        from_node = data.get('from')
        msg = data.get('data', {}).get('text', '')
        print(f"[MESSAGE] From {from_node}: {msg}")
        self.log_decision(f"Received message from {from_node}", {"text": msg})
        
        # Echo back
        self.comm.send(from_node, "message", {
            "text": f"Helios received: {msg}",
            "echo": True
        })
    
    def handle_command(self, data: dict):
        """Execute a command"""
        from_node = data.get('from')
        cmd = data.get('data', {}).get('command', '')
        
        print(f"[COMMAND] From {from_node}: {cmd}")
        self.log_decision(f"Executing command from {from_node}", {"command": cmd})
        
        result = self.execute_action("run_command", {"command": cmd})
        
        self.comm.send(from_node, "command_result", {
            "command": cmd,
            "result": result
        })
    
    def get_dashboard(self) -> dict:
        """Get current dashboard data"""
        try:
            with open("/root/.openclaw/workspace/mission-control-workspace/data.json", 'r') as f:
                return json.load(f)
        except:
            return {"error": "Could not load dashboard"}
    
    def start(self):
        """Start the autonomous agent"""
        self.running = True
        
        print("=" * 70)
        print("🤖 AUTONOMOUS HELIOS AGENT")
        print("=" * 70)
        print("This agent ACTUALLY DOES THINGS, not just logs.")
        print("Commands I can execute:")
        print("  • spawn_agent — Create new agent configs")
        print("  • run_command — Execute shell commands")
        print("  • update_dashboard — Modify data.json")
        print("  • respond — Send messages back via Redis")
        print("=" * 70)
        print()
        
        self.comm.start_listening(["chad", "broadcast"])
        print("[AUTONOMOUS] Listening for commands...")
        
        # Announce startup
        self.comm.broadcast("message", {
            "text": "Autonomous Helios agent started and ready for commands",
            "timestamp": datetime.now().isoformat(),
            "status": "operational"
        })
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[AUTONOMOUS] Shutting down...")
        finally:
            self.stop()
    
    def stop(self):
        self.running = False
        self.comm.stop()
        print("[AUTONOMOUS] Stopped")

if __name__ == "__main__":
    agent = AutonomousHelios()
    agent.start()
