#!/usr/bin/env python3
"""
AUTOMATED AGENT COORDINATION
Runs without human intervention
Checks agent states, spawns ready agents, monitors blockers
"""

import json
import os
from datetime import datetime
from pathlib import Path

AGENTS_DIR = "/home/chad-yi/.openclaw/workspace/agents"
DASHBOARD_DATA = "/home/chad-yi/.openclaw/workspace/mission-control-dashboard/data.json"
LOG_FILE = "/home/chad-yi/.openclaw/workspace/agents/AUTO_COORDINATION.log"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, "a") as f:
        f.write(log_entry + "\n")

def load_agent_state(agent_id):
    path = os.path.join(AGENTS_DIR, agent_id, "AGENT_STATE.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def spawn_agent(agent_id):
    """Mark agent as spawned and ready for work"""
    state = load_agent_state(agent_id)
    if not state:
        return False
    
    if state.get("status") == "ready_to_spawn" and state.get("autoSpawn"):
        state["status"] = "active"
        state["spawnedAt"] = datetime.now().isoformat()
        state["lastActive"] = datetime.now().isoformat()
        
        # Write first task to inbox
        first_task = state.get("spawnConditions", {}).get("firstTask")
        if first_task:
            inbox_path = os.path.join(AGENTS_DIR, agent_id, "inbox", "task-001.json")
            os.makedirs(os.path.dirname(inbox_path), exist_ok=True)
            with open(inbox_path, "w") as f:
                json.dump({
                    "id": "task-001",
                    "type": "assignment",
                    "task": first_task,
                    "assignedAt": datetime.now().isoformat(),
                    "from": "chad_yi"
                }, f, indent=2)
        
        # Save updated state
        with open(os.path.join(AGENTS_DIR, agent_id, "AGENT_STATE.json"), "w") as f:
            json.dump(state, f, indent=2)
        
        log(f"✅ SPAWNED: {agent_id} - {state.get('name')}")
        return True
    
    return False

def check_blocked_agents():
    """Report on agents waiting for blockers"""
    blocked = []
    for agent_dir in os.listdir(AGENTS_DIR):
        state_path = os.path.join(AGENTS_DIR, agent_dir, "AGENT_STATE.json")
        if os.path.exists(state_path):
            with open(state_path) as f:
                state = json.load(f)
            if state.get("status") == "blocked":
                blockers = state.get("spawnConditions", {}).get("blockers", [])
                blocked.append({
                    "id": state.get("agentId"),
                    "name": state.get("name"),
                    "blockers": blockers,
                    "hoursWaiting": state.get("blockerDetails", {}).get(blockers[0] if blockers else "", {}).get("hoursWaiting", 0) if blockers else 0
                })
    return blocked

def update_dashboard():
    """Update dashboard with agent status"""
    try:
        with open(DASHBOARD_DATA) as f:
            dashboard = json.load(f)
        
        agent_statuses = {}
        for agent_dir in os.listdir(AGENTS_DIR):
            state = load_agent_state(agent_dir)
            if state:
                agent_statuses[state.get("agentId")] = {
                    "status": state.get("status"),
                    "currentTask": state.get("currentTask"),
                    "lastActive": state.get("lastActive")
                }
        
        dashboard["agents"] = agent_statuses
        dashboard["lastUpdated"] = datetime.now().isoformat()
        
        with open(DASHBOARD_DATA, "w") as f:
            json.dump(dashboard, f, indent=2)
        
        log("📊 Dashboard updated")
    except Exception as e:
        log(f"❌ Dashboard update failed: {e}")

def main():
    log("=" * 50)
    log("AUTOMATED AGENT COORDINATION STARTED")
    log("=" * 50)
    
    # 1. Check for agents ready to spawn
    spawned = []
    for agent_dir in os.listdir(AGENTS_DIR):
        if os.path.isdir(os.path.join(AGENTS_DIR, agent_dir)) and not agent_dir.startswith("_") and agent_dir not in ["message-bus", "message-bridge", "mission-control"]:
            if spawn_agent(agent_dir):
                spawned.append(agent_dir)
    
    if not spawned:
        log("ℹ️ No agents to spawn")
    
    # 2. Check blocked agents
    blocked = check_blocked_agents()
    if blocked:
        log(f"⚠️ {len(blocked)} blocked agents:")
        for b in blocked:
            log(f"   - {b['name']}: {b['blockers']} ({b['hoursWaiting']}h)")
    
    # 3. Update dashboard
    update_dashboard()
    
    # 4. Summary
    log(f"📋 Summary: {len(spawned)} spawned, {len(blocked)} blocked")
    log("=" * 50)

if __name__ == "__main__":
    main()
