#!/usr/bin/env python3
"""
Agent Communication Hub (ACH)
Simple socket-based message bus for agents
Replaces broken ACP with working TCP sockets
"""

import socket
import threading
import json
import time
from datetime import datetime
from pathlib import Path

DB_PATH = Path("/home/chad-yi/.openclaw/workspace/mission-control-dashboard/mc.db")

class AgentMessageHub:
    """Central message hub for all agents"""
    
    def __init__(self, host='localhost', port=9999):
        self.host = host
        self.port = port
        self.agents = {}  # name -> connection
        self.message_queue = []
        self.running = False
        
    def log(self, msg):
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[HUB] {timestamp} {msg}")
        
    def start(self):
        """Start the message hub"""
        self.running = True
        
        # Create socket server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.server.listen(10)
        
        self.log(f"Agent Hub started on {self.host}:{self.port}")
        
        # Accept connections
        while self.running:
            try:
                client, addr = self.server.accept()
                thread = threading.Thread(target=self.handle_agent, args=(client, addr))
                thread.daemon = True
                thread.start()
            except Exception as e:
                self.log(f"Accept error: {e}")
                
    def handle_agent(self, client, addr):
        """Handle individual agent connection"""
        agent_name = None
        
        try:
            while self.running:
                # Receive message
                data = client.recv(4096).decode('utf-8')
                if not data:
                    break
                    
                # Parse message
                try:
                    msg = json.loads(data)
                    msg_type = msg.get('type')
                    
                    if msg_type == 'register':
                        agent_name = msg.get('agent')
                        self.agents[agent_name] = client
                        self.log(f"Agent registered: {agent_name}")
                        
                        # Send confirmation
                        self.send_to_agent(agent_name, {
                            'type': 'registered',
                            'message': f'Welcome {agent_name}'
                        })
                        
                    elif msg_type == 'heartbeat':
                        # Update agent status in database
                        self.update_agent_heartbeat(agent_name, msg)
                        
                    elif msg_type == 'task_complete':
                        # Broadcast to CHAD_YI
                        self.broadcast({
                            'type': 'notification',
                            'from': agent_name,
                            'message': f"Task completed: {msg.get('task')}"
                        })
                        
                    elif msg_type == 'log':
                        # Store log in database
                        self.store_log(agent_name, msg.get('level', 'info'), msg.get('message'))
                        
                    elif msg_type == 'message':
                        # Route to specific agent
                        to_agent = msg.get('to')
                        if to_agent in self.agents:
                            self.send_to_agent(to_agent, msg)
                        else:
                            # Store for later delivery
                            self.message_queue.append(msg)
                            
                except json.JSONDecodeError:
                    self.log(f"Invalid JSON from {agent_name}: {data[:50]}")
                    
        except Exception as e:
            self.log(f"Agent {agent_name} error: {e}")
        finally:
            if agent_name and agent_name in self.agents:
                del self.agents[agent_name]
                self.log(f"Agent disconnected: {agent_name}")
            client.close()
            
    def send_to_agent(self, agent_name, message):
        """Send message to specific agent"""
        if agent_name in self.agents:
            try:
                client = self.agents[agent_name]
                data = json.dumps(message).encode('utf-8')
                client.send(data)
                return True
            except Exception as e:
                self.log(f"Failed to send to {agent_name}: {e}")
        return False
        
    def broadcast(self, message):
        """Broadcast to all agents"""
        for agent_name in list(self.agents.keys()):
            self.send_to_agent(agent_name, message)
            
    def update_agent_heartbeat(self, agent_name, data):
        """Update agent status in database"""
        import sqlite3
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO agents (name, status, last_heartbeat, current_task)
                VALUES (?, 'active', datetime('now'), ?)
            ''', (agent_name, data.get('current_task')))
            conn.commit()
            conn.close()
        except Exception as e:
            self.log(f"DB error: {e}")
            
    def store_log(self, agent_name, level, message):
        """Store agent log in database"""
        import sqlite3
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO agent_logs (agent_name, level, message)
                VALUES (?, ?, ?)
            ''', (agent_name, level, message))
            conn.commit()
            conn.close()
        except Exception as e:
            self.log(f"Log error: {e}")

if __name__ == "__main__":
    hub = AgentMessageHub()
    hub.start()
