#!/usr/bin/env python3
"""
Example: Forger Agent using AgentClient
Connects to hub, receives tasks, sends updates
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent_client import AgentClient

class ForgerAgent(AgentClient):
    """Forger agent with custom task handling"""
    
    def __init__(self):
        super().__init__('forger')
        
    def on_task(self, task_msg):
        """Handle incoming build tasks"""
        self.log(f"Processing task: {task_msg}")
        
        # Build website
        task_id = task_msg.get('task_id')
        self.build_website(task_msg)
        
        # Report completion
        self.report_task_complete(task_id, {'status': 'success'})
        
    def build_website(self, task):
        """Build website logic"""
        # Your existing builder code here
        self.log("Building website...")
        time.sleep(2)  # Simulate work
        self.log("Build complete!")
        
if __name__ == "__main__":
    agent = ForgerAgent()
    
    if agent.connect():
        print("Forger connected. Waiting for tasks...")
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            agent.disconnect()
            print("Forger stopped")
    else:
        print("Failed to connect")
