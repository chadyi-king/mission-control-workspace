# TASK UPDATE PROCEDURE - CHAD_YI
## Follow this EVERY time a task status changes

---

## When User Says "Mark [Task] as Done"

### Step 1: Update Task Object
```python
# Edit data.json
tasks[task_id]["status"] = "done"
tasks[task_id]["completedAt"] = datetime.now().isoformat()
```

### Step 2: Move in Workflow
```python
# Remove from old workflow
if task_id in workflow["pending"]:
    workflow["pending"].remove(task_id)
if task_id in workflow["active"]:
    workflow["active"].remove(task_id)
if task_id in workflow["review"]:
    workflow["review"].remove(task_id)

# Add to done
if task_id not in workflow["done"]:
    workflow["done"].append(task_id)
```

### Step 3: Update Stats
```python
# Recalculate from workflow
stats["pending"] = len(workflow["pending"])
stats["active"] = len(workflow["active"])
stats["review"] = len(workflow["review"])
stats["done"] = len(workflow["done"])
stats["totalTasks"] = stats["pending"] + stats["active"] + stats["review"] + stats["done"] + stats["backlog"]
```

### Step 4: Update Timestamp
```python
data["lastUpdated"] = datetime.now().isoformat()
data["updatedBy"] = "CHAD_YI"
```

### Step 5: Commit and Push (CRITICAL)
```bash
cd ~/.openclaw/workspace/mission-control-dashboard
git add data.json
git commit -m "Mark [TASK_ID] as done - [brief description]"
git push
```

### Step 6: Verify
```bash
# Check GitHub
# Wait 30 seconds
# Check dashboard URL
# Confirm update
```

---

## When User Says "Start [Task]" (Pending → Active)

Same steps, but:
- Move from workflow["pending"] to workflow["active"]
- status = "active"
- NO completedAt

---

## When User Says "Send [Task] for Review" (Active → Review)

Same steps, but:
- Move from workflow["active"] to workflow["review"]
- status = "review"
- NO completedAt

---

## Automated Verification Script

Create file: `verify_task_update.py`

```python
import json
from datetime import datetime

def verify_data_integrity():
    with open('data.json') as f:
        data = json.load(f)
    
    errors = []
    
    # Check 1: Workflow counts match stats
    actual_pending = len(data['workflow']['pending'])
    actual_active = len(data['workflow']['active'])
    actual_review = len(data['workflow']['review'])
    actual_done = len(data['workflow']['done'])
    
    if actual_pending != data['stats']['pending']:
        errors.append(f"Pending mismatch: workflow={actual_pending}, stats={data['stats']['pending']}")
    
    if actual_active != data['stats']['active']:
        errors.append(f"Active mismatch: workflow={actual_active}, stats={data['stats']['active']}")
    
    # Check 2: No done tasks in pending/active
    for task_id in data['workflow']['pending']:
        if data['tasks'].get(task_id, {}).get('status') == 'done':
            errors.append(f"{task_id}: status=done but in workflow.pending")
    
    # Check 3: Timestamp is recent
    last_updated = data.get('lastUpdated', '')
    if last_updated:
        try:
            last_dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            minutes_ago = (datetime.utcnow() - last_dt.replace(tzinfo=None)).total_seconds() / 60
            if minutes_ago > 60:
                errors.append(f"Data stale: last updated {int(minutes_ago)} min ago")
        except:
            pass
    
    if errors:
        print("ERRORS FOUND:")
        for e in errors:
            print(f"  - {e}")
        return False
    else:
        print("✅ Data integrity verified")
        return True

if __name__ == "__main__":
    verify_data_integrity()
```

---

## Pre-Flight Checklist (Before Telling User "Done")

- [ ] Task object updated
- [ ] Workflow arrays correct
- [ ] Stats recalculated
- [ ] Timestamp updated
- [ ] Saved to data.json
- [ ] `git add data.json`
- [ ] `git commit -m "..."`
- [ ] `git push` (verify success)
- [ ] Dashboard shows update (wait 30s, refresh)
- [ ] Tell user: "✅ Task updated and pushed to dashboard"

---

## Common Mistakes to Avoid

❌ Only updating task object, not workflow
❌ Only updating workflow, not stats
❌ Forgetting to update timestamp
❌ Saving file but not committing
❌ Committing but not pushing
❌ Assuming push succeeded without checking

---

## Memory Note

**If I fail to push again, the user will lose trust. This is CRITICAL.**

Every task update MUST include git push.
No exceptions.
