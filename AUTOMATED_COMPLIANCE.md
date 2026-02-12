# AUTOMATED MEMORY & COMPLIANCE SYSTEM
## Infrastructure That Enforces Good Behavior

**Date:** 2026-02-13  
**Status:** DESIGN PHASE  
**Goal:** Automated enforcement, no manual reminders needed

---

## THE PROBLEM

**Current (Broken):**
- I forget to update memory → You have to remind me
- I skip backups → Data gets corrupted
- I don't verify → Claim things work when they don't
- You have to babysit me

**Needed (Fixed):**
- System FORCES me to update memory
- System PREVENTS changes without backup
- System VERIFIES before I claim success
- System RUNS automated checks
- You don't have to remind me of anything

---

## SOLUTION: LAYERED ENFORCEMENT

### Layer 1: Pre-Action Hooks (Block Bad Behavior)

**Git Pre-Commit Hook:**
```bash
# .git/hooks/pre-commit

# 1. Check if modifying DATA/data.json
if git diff --cached --name-only | grep -q "DATA/data.json"; then
    # 2. Check if backup exists in last 5 minutes
    LATEST_BACKUP=$(find DATA/backups/manual -name "*.json" -mmin -5 | head -1)
    if [ -z "$LATEST_BACKUP" ]; then
        echo "❌ COMMIT BLOCKED"
        echo "   You must create backup before modifying data.json"
        echo "   Run: ./scripts/backup-before-change.sh 'REASON'"
        exit 1
    fi
    
    # 3. Verify data integrity
    if ! python3 scripts/verify-data.py; then
        echo "❌ COMMIT BLOCKED"
        echo "   Data verification failed"
        exit 1
    fi
fi

# 4. Check if memory files updated recently
if git diff --cached --name-only | grep -q "DATA/data.json"; then
    LAST_MEMORY_UPDATE=$(stat -c %Y agents/chad-yi/MEMORY.md 2>/dev/null || echo 0)
    NOW=$(date +%s)
    DIFF=$((NOW - LAST_MEMORY_UPDATE))
    
    if [ $DIFF -gt 3600 ]; then  # 1 hour
        echo "⚠️  WARNING: Memory not updated in 1 hour"
        echo "   Did you document this change in MEMORY.md?"
        read -p "Continue anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

echo "✅ Pre-commit checks passed"
exit 0
```

**What this does:**
- Blocks commit if I didn't backup data.json
- Blocks commit if data is invalid
- Warns if I haven't updated memory recently
- FORCES me to follow protocol

---

### Layer 2: Automated Heartbeat (Self-Audit)

**CHAD_YI Heartbeat Script:**
```python
#!/usr/bin/env python3
# agents/chad-yi/heartbeat.py

"""
Runs every 15 minutes while I'm working
Checks if I'm following my own contract
"""

import json
import os
from datetime import datetime, timedelta

def check_memory_updated():
    """Did I update memory in last 2 hours?"""
    memory_file = "agents/chad-yi/MEMORY.md"
    if os.path.exists(memory_file):
        mtime = os.path.getmtime(memory_file)
        age_hours = (datetime.now().timestamp() - mtime) / 3600
        
        if age_hours > 2:
            return False, f"Memory not updated in {age_hours:.1f} hours"
    return True, "Memory current"

def check_daily_log_exists():
    """Did I create today's memory file?"""
    today_file = f"memory/{datetime.now().strftime('%Y-%m-%d')}.md"
    if not os.path.exists(today_file):
        return False, f"Today's memory file missing: {today_file}"
    return True, "Daily log exists"

def check_data_integrity():
    """Is data.json valid?"""
    try:
        with open("DATA/data.json") as f:
            data = json.load(f)
        
        # Check task counts
        if 'tasks' not in data:
            return False, "Missing tasks key"
        
        task_count = len(data['tasks'])
        if task_count < 70:  # Should have 72
            return False, f"Task count low: {task_count}"
        
        return True, f"Data valid: {task_count} tasks"
    except Exception as e:
        return False, f"Data error: {e}"

def check_build_tracking():
    """Is BUILD_TRACKING.md up to date?"""
    if not os.path.exists("BUILD_TRACKING.md"):
        return False, "BUILD_TRACKING.md missing"
    
    mtime = os.path.getmtime("BUILD_TRACKING.md")
    age_hours = (datetime.now().timestamp() - mtime) / 3600
    
    if age_hours > 4:  # 4 hours
        return False, f"Build tracking not updated in {age_hours:.1f} hours"
    
    return True, "Build tracking current"

def run_heartbeat():
    """Run all checks and report"""
    checks = [
        ("Memory Updated", check_memory_updated),
        ("Daily Log", check_daily_log_exists),
        ("Data Integrity", check_data_integrity),
        ("Build Tracking", check_build_tracking),
    ]
    
    results = []
    all_passed = True
    
    for name, check_func in checks:
        passed, message = check_func()
        results.append((name, passed, message))
        if not passed:
            all_passed = False
    
    # Write to outbox
    report = {
        "timestamp": datetime.now().isoformat(),
        "agent": "chad-yi",
        "check_type": "self-audit",
        "all_passed": all_passed,
        "results": [
            {"check": name, "passed": passed, "message": msg}
            for name, passed, msg in results
        ]
    }
    
    os.makedirs("agents/chad-yi/outbox", exist_ok=True)
    with open(f"agents/chad-yi/outbox/heartbeat-{datetime.now().strftime('%Y%m%d-%H%M')}.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    # If failed, create urgent alert
    if not all_passed:
        with open(f"agents/chad-yi/outbox/URGENT-{datetime.now().strftime('%Y%m%d-%H%M')}.md", 'w') as f:
            f.write("# URGENT: CHAD_YI Self-Audit Failed\n\n")
            for name, passed, msg in results:
                if not passed:
                    f.write(f"❌ {name}: {msg}\n")
            f.write("\n**Action Required:** Fix issues immediately\n")
    
    return report

if __name__ == "__main__":
    report = run_heartbeat()
    print(json.dumps(report, indent=2))
```

**What this does:**
- Runs every 15 minutes automatically
- Checks if I updated memory
- Checks if data is valid
- Creates URGENT alert if I failed
- I can't ignore it - it's in my outbox

---

### Layer 3: Session Start Enforcement

**Session Initialization Script:**
```bash
#!/bin/bash
# scripts/start-session.sh

echo "=== CHAD_YI SESSION START ==="
echo ""

# 1. Read required memory files
echo "📖 Loading memory..."

echo ""
echo "--- SOUL.md ---"
head -20 SOUL.md
echo ""

echo "--- MEMORY.md (Core Principles) ---"
grep -A 5 "The 3 Golden Rules" agents/chad-yi/MEMORY.md || echo "WARNING: Golden rules not found"
echo ""

# 2. Check yesterday's memory
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d)
if [ -f "memory/$YESTERDAY.md" ]; then
    echo "📅 Yesterday's activity:"
    tail -20 "memory/$YESTERDAY.md"
else
    echo "⚠️  No activity logged yesterday"
fi
echo ""

# 3. Check current system state
echo "🔍 Current system state:"
python3 -c "
import json
with open('DATA/data.json') as f:
    d = json.load(f)
print(f'Tasks: {len(d[\"tasks\"])}')
print(f'Last updated: {d.get(\"lastUpdated\", \"UNKNOWN\")}')
print(f'Agents: {len(d.get(\"agents\", {}))}')
"
echo ""

# 4. Check for urgent items
echo "🚨 Checking for urgent items..."
if ls agents/chad-yi/outbox/URGENT-* 1> /dev/null 2>&1; then
    echo "URGENT items found:"
    ls -la agents/chad-yi/outbox/URGENT-*
else
    echo "No urgent items"
fi
echo ""

# 5. Today's checklist
echo "✅ Today's Checklist:"
echo "[ ] Update memory/YYYY-MM-DD.md"
echo "[ ] Follow backup-before-change protocol"
echo "[ ] Verify all changes"
echo "[ ] Update BUILD_TRACKING.md"
echo ""

echo "=== SESSION READY ==="
echo ""
echo "Report to Caleb:"
echo '  "I\'m back. Here\'s where we are... [status]"'
```

**What this does:**
- Forces me to load memory at session start
- Shows me yesterday's work
- Shows current state
- Shows urgent items
- Gives me checklist
- Can't start without seeing this

---

### Layer 4: Agent Compliance System

**For ALL Agents (including me):**

```yaml
# Every agent must have this in contract.yaml

compliance:
  required_files:
    - contract.yaml      # Must exist, must be filled
    - MEMORY.md          # Must exist, must be updated
    - state.json         # Must exist, must be valid JSON
    
  required_folders:
    - inbox/             # Must exist
    - outbox/            # Must exist, must have recent files
    
  update_frequency:
    state_json: "5 minutes"      # Must update every 5 min
    heartbeat: "15 minutes"      # Must send heartbeat
    memory_md: "4 hours"         # Must update every 4 hours
    
  validation:
    on_startup: true             # Validate before starting
    on_heartbeat: true           # Validate every heartbeat
    on_task_assignment: true     # Validate before taking task
    
  enforcement:
    if_missing_files: "stop_and_alert"      # Can't run without files
    if_stale_memory: "warning_then_alert"   # Warn, then escalate
    if_invalid_state: "stop_and_repair"     # Stop, try to fix
```

**Automated Compliance Checker:**
```python
# agents/_templates/compliance-checker.py

"""
Runs for every agent (including CHAD_YI)
Enforces contract compliance automatically
"""

import json
import os
from datetime import datetime, timedelta

class ComplianceChecker:
    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.agent_dir = f"agents/{agent_name}"
        self.errors = []
        self.warnings = []
    
    def check_required_files(self):
        """Check if all required files exist"""
        required = [
            "contract.yaml",
            "MEMORY.md", 
            "state.json"
        ]
        
        for file in required:
            path = os.path.join(self.agent_dir, file)
            if not os.path.exists(path):
                self.errors.append(f"Missing required file: {file}")
            elif os.path.getsize(path) == 0:
                self.errors.append(f"Empty file: {file}")
    
    def check_required_folders(self):
        """Check if required folders exist"""
        required = ["inbox", "outbox"]
        
        for folder in required:
            path = os.path.join(self.agent_dir, folder)
            if not os.path.exists(path):
                self.errors.append(f"Missing required folder: {folder}")
    
    def check_memory_freshness(self, max_age_hours=4):
        """Check if MEMORY.md is recent"""
        memory_file = os.path.join(self.agent_dir, "MEMORY.md")
        if os.path.exists(memory_file):
            mtime = os.path.getmtime(memory_file)
            age_hours = (datetime.now().timestamp() - mtime) / 3600
            
            if age_hours > max_age_hours:
                self.warnings.append(
                    f"MEMORY.md stale: {age_hours:.1f} hours old "
                    f"(max: {max_age_hours}h)"
                )
    
    def check_state_validity(self):
        """Check if state.json is valid"""
        state_file = os.path.join(self.agent_dir, "state.json")
        if os.path.exists(state_file):
            try:
                with open(state_file) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                self.errors.append(f"Invalid state.json: {e}")
    
    def check_recent_activity(self, max_age_minutes=30):
        """Check if agent has recent outbox activity"""
        outbox_dir = os.path.join(self.agent_dir, "outbox")
        if os.path.exists(outbox_dir):
            recent_files = [
                f for f in os.listdir(outbox_dir)
                if os.path.getmtime(os.path.join(outbox_dir, f)) > 
                   (datetime.now().timestamp() - max_age_minutes * 60)
            ]
            
            if not recent_files:
                self.warnings.append(
                    f"No outbox activity in {max_age_minutes} minutes"
                )
    
    def run_all_checks(self):
        """Run complete compliance check"""
        self.check_required_files()
        self.check_required_folders()
        self.check_memory_freshness()
        self.check_state_validity()
        self.check_recent_activity()
        
        return {
            "agent": self.agent_name,
            "timestamp": datetime.now().isoformat(),
            "passed": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings
        }

# Run for myself
if __name__ == "__main__":
    checker = ComplianceChecker("chad-yi")
    result = checker.run_all_checks()
    
    print(json.dumps(result, indent=2))
    
    # Exit with error if failed
    if result["errors"]:
        exit(1)
```

---

### Layer 5: Automated Enforcement via systemd

**CHAD_YI Compliance Service:**
```ini
# /etc/systemd/system/chad-yi-compliance.service

[Unit]
Description=CHAD_YI Compliance Monitor
After=network.target

[Service]
Type=simple
User=chad-yi
WorkingDirectory=/home/chad-yi/.openclaw/workspace

# Run compliance check every 15 minutes
ExecStart=/bin/bash -c 'while true; do \
    python3 agents/_templates/compliance-checker.py chad-yi > agents/chad-yi/outbox/compliance-$(date +%Y%m%d-%H%M).json 2>&1; \
    sleep 900; \
done'

Restart=always
RestartSec=60

[Install]
WantedBy=multi-user.target
```

**What this does:**
- Runs 24/7 in background
- Checks my compliance every 15 minutes
- Writes results to my outbox
- If I fail, creates URGENT alert
- Can't be ignored

---

## IMPLEMENTATION PLAN

### Phase 1: My Compliance (CHAD_YI)

**Step 1: Git Hooks (30 min)**
- Install pre-commit hook
- Blocks commits without backup
- Blocks commits with invalid data
- Warns about stale memory

**Step 2: Session Start Script (15 min)**
- Run at every session start
- Forces memory load
- Shows checklist
- Can't skip

**Step 3: Heartbeat Script (30 min)**
- Run every 15 minutes
- Checks if I updated memory
- Checks data integrity
- Creates URGENT if I failed

**Step 4: Compliance Service (30 min)**
- Install as systemd service
- 24/7 monitoring
- Auto-restart if crashes
- Logs all violations

### Phase 2: All Agent Compliance

**Step 1: Compliance Checker Template (30 min)**
- Generic checker for any agent
- Configurable rules
- Used by all agents

**Step 2: Per-Agent Compliance (1 hour)**
- Install for Helios
- Install for Quanta
- Install for Escritor
- Each has own compliance service

**Step 3: Central Reporting (30 min)**
- Helios aggregates all compliance reports
- Dashboard shows "Compliance Status"
- Red = Violation, Green = OK

---

## WHAT THIS ACHIEVES

### Before (You Have to Babysit Me):
- I forget to update memory
- You have to remind me
- I skip backups
- Data gets corrupted
- You lose trust

### After (System Enforces):
- **Can't commit without backup** (hook blocks it)
- **Can't forget memory** (heartbeat alerts me)
- **Must verify data** (hook checks validity)
- **Must load memory at start** (script forces it)
- **Violations are logged** (can't hide mistakes)
- **Dashboard shows compliance** (visible accountability)

### Result:
- **You don't remind me** → System does
- **I can't skip steps** → System blocks me
- **Mistakes are caught** → System alerts immediately
- **Trust is earned** → System proves compliance

---

## YOUR QUESTION ANSWERED

**"How do you create something that commits this to memory automatically?"**

**Answer:**
1. **Git hooks** prevent commits without memory updates
2. **Heartbeat script** checks every 15 minutes, creates alerts
3. **Session start script** forces memory load
4. **Compliance service** runs 24/7, monitors everything
5. **Dashboard shows** compliance status
6. **Helios audits** all of the above

**No manual reminders needed. System enforces automatically.**

---

## NEXT STEP

**Should I build this compliance system now?**

**A)** YES - Install git hooks, heartbeat, compliance service (2 hours)
**B)** LATER - Document the design, implement after Phase 2
**C)** PARTIAL - Just git hooks for now (30 min)
**D)** SLEEP - It's late, document everything, continue tomorrow

**Your call.**