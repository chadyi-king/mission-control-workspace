#!/usr/bin/env python3
"""
Agent Orchestrator - Manages all agents via Redis communication
"""

import json
import time
import threading
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from sync.redis_comm import RedisComm

class AgentOrchestrator:
    """Central orchestrator for all agents"""
    
    def __init__(self, node_name: str = "helios"):
        self.node_name = node_name
        self.comm = RedisComm(node_name=node_name, use_rest=True)
        self.agents: Dict[str, Any] = {}
        self.tasks: Dict[str, Any] = {}
        self.running = False
        self.data_file = "/root/.openclaw/workspace/mission-control-workspace/data.json"
        
        # Register handlers
        self.comm.on("agent_register", self._handle_agent_register)
        self.comm.on("agent_status", self._handle_agent_status)
        self.comm.on("task_request", self._handle_task_request)
        self.comm.on("task_complete", self._handle_task_complete)
        self.comm.on("heartbeat", self._handle_heartbeat)
        self.comm.on("alert", self._handle_alert)
        
    def _load_data(self) -> dict:
        """Load dashboard data"""
        try:
            with open(self.data_file, 'r') as f:
                return json.load(f)
        except:
            return self._create_default_data()
    
    def _save_data(self, data: dict):
        """Save dashboard data"""
        data['lastUpdated'] = datetime.now().isoformat()
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _create_default_data(self) -> dict:
        """Create default dashboard data"""
        return {
            "schema": "mission.control.dashboard.v1",
            "lastUpdated": datetime.now().isoformat(),
            "system": {"status": "initializing", "version": "1.0.0"},
            "agents": {},
            "tasks": {"total": 0, "pending": 0, "active": 0, "done": 0},
            "health": {"alerts": [], "warnings": []}
        }
    
    def _handle_agent_register(self, data: dict):
        """Handle agent registration"""
        agent_id = data['data'].get('agent_id')
        agent_info = data['data'].get('info', {})
        
        dashboard_data = self._load_data()
        dashboard_data['agents'][agent_id] = {
            **agent_info,
            'status': 'active',
            'last_seen': datetime.now().isoformat(),
            'registered_at': datetime.now().isoformat()
        }
        self._save_data(dashboard_data)
        
        print(f"[ORCHESTRATOR] Agent registered: {agent_id}")
        
        # Acknowledge
        self.comm.send(data['from'], "ack", {
            "type": "agent_registered",
            "agent_id": agent_id
        })
    
    def _handle_agent_status(self, data: dict):
        """Handle agent status update"""
        agent_id = data['data'].get('agent_id')
        status = data['data'].get('status')
        
        dashboard_data = self._load_data()
        if agent_id in dashboard_data['agents']:
            dashboard_data['agents'][agent_id]['status'] = status
            dashboard_data['agents'][agent_id]['last_seen'] = datetime.now().isoformat()
            self._save_data(dashboard_data)
            
        print(f"[ORCHESTRATOR] Agent {agent_id} status: {status}")
    
    def _handle_task_request(self, data: dict):
        """Handle task request from agent"""
        task = data['data'].get('task', {})
        task_id = task.get('id', f"task-{int(time.time())}")
        
        dashboard_data = self._load_data()
        dashboard_data['tasks']['pending'] += 1
        dashboard_data['tasks']['total'] += 1
        
        # Store task
        if 'task_queue' not in dashboard_data:
            dashboard_data['task_queue'] = []
        dashboard_data['task_queue'].append({
            **task,
            'id': task_id,
            'status': 'pending',
            'requested_by': data['from'],
            'created_at': datetime.now().isoformat()
        })
        
        self._save_data(dashboard_data)
        
        print(f"[ORCHESTRATOR] Task requested: {task_id}")
        
        # Route to appropriate agent
        self._route_task(task)
    
    def _handle_task_complete(self, data: dict):
        """Handle task completion"""
        task_id = data['data'].get('task_id')
        result = data['data'].get('result', {})
        
        dashboard_data = self._load_data()
        dashboard_data['tasks']['active'] -= 1
        dashboard_data['tasks']['done'] += 1
        
        # Update agent stats
        agent_id = data['from']
        if agent_id in dashboard_data['agents']:
            dashboard_data['agents'][agent_id]['tasks_completed'] = \
                dashboard_data['agents'][agent_id].get('tasks_completed', 0) + 1
            dashboard_data['agents'][agent_id]['tasks_active'] = \
                max(0, dashboard_data['agents'][agent_id].get('tasks_active', 0) - 1)
        
        self._save_data(dashboard_data)
        
        print(f"[ORCHESTRATOR] Task completed: {task_id}")
        
        # Notify Caleb if critical
        if result.get('critical'):
            self.comm.broadcast("notify_caleb", {
                "message": f"Critical task completed: {task_id}",
                "result": result
            })
    
    def _handle_heartbeat(self, data: dict):
        """Handle agent heartbeat"""
        agent_id = data['from']
        dashboard_data = self._load_data()
        
        if agent_id in dashboard_data['agents']:
            dashboard_data['agents'][agent_id]['last_seen'] = datetime.now().isoformat()
            self._save_data(dashboard_data)
    
    def _handle_alert(self, data: dict):
        """Handle alert from agent"""
        alert = data['data']
        level = alert.get('level', 'info')
        message = alert.get('message', '')
        
        print(f"[ORCHESTRATOR] ALERT [{level}]: {message}")
        
        # Add to dashboard
        dashboard_data = self._load_data()
        if level == 'critical':
            dashboard_data['health']['alerts'].append({
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'from': data['from']
            })
        else:
            dashboard_data['health']['warnings'].append({
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'from': data['from']
            })
        self._save_data(dashboard_data)
        
        # Broadcast to all
        self.comm.broadcast("alert", alert)
    
    def _route_task(self, task: dict):
        """Route task to appropriate agent"""
        task_type = task.get('type', 'general')
        
        # Simple routing logic
        routing_map = {
            'writing': 'ESCRITOR',
            'trading': 'QUANTA',
            'monitoring': 'MENSAMUSA',
            'scripting': 'AUTOUR',
            'design': 'FORGER'
        }
        
        target_agent = routing_map.get(task_type, 'CHAD_YI')
        
        self.comm.send(target_agent.lower(), "task_assigned", {
            'task': task,
            'assigned_by': self.node_name,
            'assigned_at': datetime.now().isoformat()
        })
        
        print(f"[ORCHESTRATOR] Task routed to {target_agent}")
    
    def spawn_agent(self, agent_id: str, agent_config: dict):
        """Spawn a new agent"""
        print(f"[ORCHESTRATOR] Spawning agent: {agent_id}")
        
        # Send spawn command via Redis
        self.comm.broadcast("spawn_agent", {
            'agent_id': agent_id,
            'config': agent_config,
            'spawned_by': self.node_name,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update dashboard
        dashboard_data = self._load_data()
        dashboard_data['agents'][agent_id] = {
            **agent_config,
            'status': 'spawning',
            'spawned_at': datetime.now().isoformat()
        }
        self._save_data(dashboard_data)
    
    def kill_agent(self, agent_id: str):
        """Kill an agent"""
        print(f"[ORCHESTRATOR] Killing agent: {agent_id}")
        
        self.comm.send(agent_id.lower(), "kill", {
            'reason': 'orchestrator_command',
            'timestamp': datetime.now().isoformat()
        })
        
        # Update dashboard
        dashboard_data = self._load_data()
        if agent_id in dashboard_data['agents']:
            dashboard_data['agents'][agent_id]['status'] = 'killed'
            self._save_data(dashboard_data)
    
    def get_status(self) -> dict:
        """Get full system status"""
        return self._load_data()
    
    def start(self):
        """Start the orchestrator"""
        self.running = True
        self.comm.start_listening(['chad', 'broadcast'])
        
        print("[ORCHESTRATOR] Started")
        print("[ORCHESTRATOR] Listening for agents...")
        
        # Heartbeat thread
        def heartbeat():
            while self.running:
                self.comm.broadcast("heartbeat", {
                    'from': self.node_name,
                    'timestamp': datetime.now().isoformat()
                })
                time.sleep(30)
        
        hb_thread = threading.Thread(target=heartbeat, daemon=True)
        hb_thread.start()
        
        # Keep running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the orchestrator"""
        self.running = False
        self.comm.stop()
        print("[ORCHESTRATOR] Stopped")

if __name__ == "__main__":
    orch = AgentOrchestrator()
    orch.start()
