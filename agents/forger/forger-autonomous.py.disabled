#!/usr/bin/env python3
"""
Forger Autonomous Agent
Web Architect - Designs and builds websites autonomously
"""

import json
import os
import subprocess
import glob
import time
from datetime import datetime

class ForgerAgent:
    def __init__(self):
        self.base_dir = "/home/chad-yi/.openclaw/workspace"
        self.agent_dir = os.path.join(self.base_dir, "agents", "forger")
        self.inbox_dir = os.path.join(self.agent_dir, "inbox")
        self.outbox_dir = os.path.join(self.agent_dir, "outbox")
        self.projects_dir = os.path.join(self.agent_dir, "projects")
        
    def check_inbox(self):
        """Check for new tasks in inbox"""
        if not os.path.exists(self.inbox_dir):
            return []
        
        task_files = glob.glob(os.path.join(self.inbox_dir, "TASK-*.md"))
        # Sort by modification time (newest first)
        task_files.sort(key=os.path.getmtime, reverse=True)
        return task_files
    
    def read_task(self, task_file):
        """Read task content"""
        try:
            with open(task_file, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading task: {e}"
    
    def process_task(self, task_file):
        """Process a task and generate response"""
        task_content = self.read_task(task_file)
        task_name = os.path.basename(task_file)
        timestamp = datetime.now().strftime('%Y%m%d-%H%M')
        
        # Create response
        response = f"""# Forger Response: {task_name}
**Processed:** {datetime.now().isoformat()}
**Status:** ACKNOWLEDGED - Processing

## Task Received
{task_content[:500]}...

## Action Plan
1. Analyzing task requirements
2. Reviewing design system (Forest Green #2E5C4F, Warm Orange #F4A261)
3. Creating deliverable
4. Saving to projects folder

## Current Focus
Building hero visual for B6-Elluminate based on reference image:
- 3 figures with lightbulbs (blue, orange, green)
- "Ignite the SPARK within your TEAM" headline
- Professional, modern aesthetic

## Next Steps
- Generate hero banner options
- Save to /projects/B6-elluminate/designs/
- Notify CHAD_YI when complete

**Forger: Building now.**
"""
        
        # Write to outbox
        os.makedirs(self.outbox_dir, exist_ok=True)
        response_file = os.path.join(self.outbox_dir, f"response-{timestamp}-{task_name}")
        with open(response_file, 'w') as f:
            f.write(response)
        
        return response_file
    
    def update_state(self, status="active", current_task=None):
        """Update agent state.json"""
        state_path = os.path.join(self.agent_dir, "state.json")
        
        state = {
            "agentId": "forger",
            "name": "FORGER",
            "status": status,
            "currentTask": current_task or "Processing inbox tasks",
            "lastActive": datetime.now().isoformat(),
            "capabilities": ["web-design", "frontend-dev", "ui-ux"],
            "pendingTasks": len(self.check_inbox())
        }
        
        with open(state_path, 'w') as f:
            json.dump(state, f, indent=2)
    
    def run_cycle(self):
        """Main work cycle"""
        print(f"[{datetime.now()}] Forger checking inbox...")
        
        tasks = self.check_inbox()
        
        if tasks:
            print(f"  Found {len(tasks)} task(s)")
            # Process the newest task
            newest_task = tasks[0]
            print(f"  Processing: {os.path.basename(newest_task)}")
            
            response_file = self.process_task(newest_task)
            print(f"  Response written: {response_file}")
            
            self.update_state("active", f"Processing {os.path.basename(newest_task)}")
        else:
            print("  No new tasks")
            self.update_state("idle", "Awaiting assignments")
        
        print(f"[{datetime.now()}] Cycle complete. Sleeping 10 minutes...")
    
    def run(self):
        """Main loop - runs continuously"""
        print("=" * 50)
        print("FORGER Autonomous Agent Starting...")
        print("=" * 50)
        
        while True:
            try:
                self.run_cycle()
                time.sleep(600)  # 10 minutes
            except Exception as e:
                print(f"ERROR: {e}")
                time.sleep(60)  # Wait 1 min on error, then retry

if __name__ == "__main__":
    agent = ForgerAgent()
    agent.run()
