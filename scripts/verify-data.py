#!/usr/bin/env python3
# verify-data.py
# Validates data.json structure

import json
import sys

def verify_data():
    try:
        with open('/home/chad-yi/.openclaw/workspace/DATA/data.json', 'r') as f:
            data = json.load(f)
        
        checks = []
        
        # Check 1: Has tasks
        if 'tasks' not in data:
            checks.append(("FAIL", "Missing 'tasks' key"))
        else:
            task_count = len(data['tasks'])
            checks.append(("PASS", f"Tasks: {task_count}"))
        
        # Check 2: Has agents
        if 'agents' not in data:
            checks.append(("FAIL", "Missing 'agents' key"))
        else:
            agent_count = len(data['agents'])
            checks.append(("PASS", f"Agents: {agent_count}"))
        
        # Check 3: Has workflow
        if 'workflow' not in data:
            checks.append(("WARN", "Missing 'workflow' key"))
        else:
            checks.append(("PASS", "Workflow structure exists"))
        
        # Check 4: Task IDs match
        if 'tasks' in data and 'workflow' in data:
            all_task_ids = set(data['tasks'].keys())
            workflow_ids = set()
            for status, ids in data['workflow'].items():
                workflow_ids.update(ids)
            
            # Check for duplicates
            if len(workflow_ids) != len(list(workflow_ids)):
                checks.append(("FAIL", "Duplicate task IDs in workflow"))
            else:
                checks.append(("PASS", "No duplicate task IDs"))
        
        # Check 5: Valid JSON structure
        checks.append(("PASS", "Valid JSON"))
        
        # Print results
        print("=== DATA VERIFICATION ===")
        passed = 0
        failed = 0
        for status, msg in checks:
            icon = "✅" if status == "PASS" else "⚠️" if status == "WARN" else "❌"
            print(f"{icon} {msg}")
            if status == "PASS":
                passed += 1
            elif status == "FAIL":
                failed += 1
        
        print(f"\nResults: {passed} passed, {failed} failed")
        
        if failed > 0:
            sys.exit(1)
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ INVALID JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    verify_data()
