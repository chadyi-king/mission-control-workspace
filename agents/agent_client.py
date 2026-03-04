#!/usr/bin/env python3
"""
Agent Client Library
Simple socket client for agents to connect to hub
"""

import socket
import json
import threading
import time
from datetime import datetime

class AgentClient:
    """Client for agents to connect to message hub"""
    
    def __init__(self, agent_name, host='localhost', port=9999):
        self.agent_name = agent_name
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.running = False
        
    def log(self, msg):
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"[{self.agent_name}] {timestamp} {msg}")
        
    def connect(self):
        """Connect to message hub"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            
            # Register with hub
            self.send({
                'type': 'register',
                'agent': self.agent_name,
                'timestamp': datetime.now().isoformat()
            })
            
            self.log(f"Connected to hub at {self.host}:{self.port}")
            
            # Start listener thread
            self.running = True
            listener = threading.Thread(target=self._listen)
            listener.daemon = True
            listener.start()
            
            # Start heartbeat
            heartbeat = threading.Thread(target=self._heartbeat)
            heartbeat.daemon = True
            heartbeat.start()
            
            return True
            
        except Exception as e:
            self.log(f"Connection failed: {e}")
            return False
            
    def _listen(self):
        """Listen for incoming messages"""
        while self.running and self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                    
                msg = json.loads(data)
                self._handle_message(msg)
                
            except Exception as e:
                if self.running:
                    self.log(f"Listen error: {e}")
                break
                
        self.connected = False
        self.log("Disconnected from hub")
        
    def _handle_message(self, msg):
        """Handle incoming message"""
        msg_type = msg.get('type')
        
        if msg_type == 'registered':
            self.log(f"Hub: {msg.get('message')}")
            
        elif msg_type == 'notification':
            self.log(f"Notification from {msg.get('from')}: {msg.get('message')}")
            
        elif msg_type == 'task':
            self.log(f"New task assigned: {msg.get('task_id')}")
            # Override this method to handle tasks
            self.on_task(msg)
            
        else:
            self.log(f"Received: {msg}")
            
    def _heartbeat(self):
        """Send periodic heartbeats"""
        while self.running and self.connected:
            time.sleep(30)  # Every 30 seconds
            self.send({
                'type': 'heartbeat',
                'agent': self.agent_name,
                'timestamp': datetime.now().isoformat()
            })
            
    def send(self, message):
        """Send message to hub"""
        if self.connected and self.socket:
            try:
                data = json.dumps(message).encode('utf-8')
                self.socket.send(data)
                return True
            except Exception as e:
                self.log(f"Send failed: {e}")
                self.connected = False
        return False
        
    def send_message(self, to_agent, content, priority='normal'):
        """Send message to another agent"""
        return self.send({
            'type': 'message',
            'from': self.agent_name,
            'to': to_agent,
            'content': content,
            'priority': priority,
            'timestamp': datetime.now().isoformat()
        })
        
    def log_message(self, level, message):
        """Send log to hub"""
        return self.send({
            'type': 'log',
            'agent': self.agent_name,
            'level': level,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
    def report_task_complete(self, task_id, result=None):
        """Report task completion"""
        return self.send({
            'type': 'task_complete',
            'agent': self.agent_name,
            'task': task_id,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    def on_task(self, task_msg):
        """Override this to handle incoming tasks"""
        pass
        
    def disconnect(self):
        """Disconnect from hub"""
        self.running = False
        self.connected = False
        if self.socket:
            self.socket.close()
            
# Convenience decorator
def connected_agent(agent_name):
    """Decorator to create connected agent"""
    def decorator(func):
        client = AgentClient(agent_name)
        if client.connect():
            return func(client)
        else:
            print(f"Failed to connect {agent_name}")
            return None
    return decorator
