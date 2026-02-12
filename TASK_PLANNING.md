# TASK PLANNING SYSTEM
## Subtasks, Checklists, and Progress Tracking

**Date:** 2026-02-13  
**Purpose:** Agents (including me) plan tasks with subtasks, track progress

---

## THE PROBLEM

**Current:**
- Task: "Build Helios service"
- No breakdown of HOW to do it
- No progress tracking
- No visibility into sub-steps

**Needed:**
- Task with subtasks
- Progress: 3 of 8 steps complete
- Blocked on: Step 4 needs Caleb input
- Time estimate per subtask
- Dependencies between subtasks

---

## SOLUTION: TASK BREAKDOWN STRUCTURE

### Data Structure (Updated)

```json
{
  "tasks": {
    "A6-4": {
      "id": "A6-4",
      "title": "Install Helios COO Service",
      "project": "A6",
      "category": "A",
      "status": "active",
      "priority": "high",
      "agent": "CHAD_YI",
      "deadline": "2026-02-14",
      
      "plan": {
        "created": "2026-02-13T00:40:00+08:00",
        "total_steps": 8,
        "completed_steps": 3,
        "estimated_hours": 4,
        "actual_hours": 2.5,
        
        "steps": [
          {
            "id": 1,
            "title": "Create Helios service file",
            "description": "Write helios.service systemd config",
            "status": "done",
            "started": "2026-02-13T00:45:00+08:00",
            "completed": "2026-02-13T00:50:00+08:00",
            "hours_actual": 0.5,
            "deliverable": "agents/helios/helios.service"
          },
          {
            "id": 2,
            "title": "Create audit script",
            "description": "Write helios-audit.py with all checks",
            "status": "done",
            "started": "2026-02-13T00:50:00+08:00",
            "completed": "2026-02-13T01:00:00+08:00",
            "hours_actual": 1.0,
            "deliverable": "agents/helios/helios-audit.py"
          },
          {
            "id": 3,
            "title": "Test audit script",
            "description": "Run locally, verify all checks work",
            "status": "done",
            "started": "2026-02-13T01:00:00+08:00",
            "completed": "2026-02-13T01:15:00+08:00",
            "hours_actual": 0.5,
            "deliverable": "Test report in outbox/"
          },
          {
            "id": 4,
            "title": "Install Ollama models",
            "description": "Pull qwen2.5:7b and llava:13b",
            "status": "blocked",
            "blocked_reason": "Needs sudo access for ollama pull",
            "started": null,
            "completed": null,
            "hours_estimated": 1.0,
            "needs_input_from": "Caleb",
            "input_request": "Please run: ollama pull qwen2.5:7b && ollama pull llava:13b"
          },
          {
            "id": 5,
            "title": "Install systemd service",
            "description": "Enable and start helios.service",
            "status": "pending",
            "depends_on": [4],
            "started": null,
            "completed": null,
            "hours_estimated": 0.5,
            "deliverable": "Service running (systemctl status helios)"
          },
          {
            "id": 6,
            "title": "Configure 15-min cron",
            "description": "Set up automatic audit cycle",
            "status": "pending",
            "depends_on": [5],
            "started": null,
            "completed": null,
            "hours_estimated": 0.5
          },
          {
            "id": 7,
            "title": "Test full audit cycle",
            "description": "Verify Helios audits all agents",
            "status": "pending",
            "depends_on": [6],
            "started": null,
            "completed": null,
            "hours_estimated": 1.0,
            "deliverable": "Audit report in agents/helios/outbox/"
          },
          {
            "id": 8,
            "title": "Update dashboard to show audit status",
            "description": "Add System Health section",
            "status": "pending",
            "depends_on": [7],
            "started": null,
            "completed": null,
            "hours_estimated": 1.0,
            "deliverable": "dashboard shows Helios reports"
          }
        ]
      },
      
      "notes": "Phase 2 implementation. Step 4 blocked on Ollama models.",
      "createdAt": "2026-02-13T00:40:00+08:00",
      "updatedAt": "2026-02-13T01:15:00+08:00"
    }
  }
}
```

---

## DASHBOARD DISPLAY

### Task Detail View (Modal)

```
┌─────────────────────────────────────────────────────┐
│  A6-4: Install Helios COO Service        [X]        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Progress: ████████░░░░ 3 of 8 steps (38%)         │
│  Time: 2.5h / 4h estimated                           │
│  Status: Active - Step 4 Blocked                    │
│                                                     │
│  STEPS:                                             │
│  ✅ 1. Create service file (30m)                    │
│  ✅ 2. Create audit script (1h)                     │
│  ✅ 3. Test script (30m)                            │
│  🔴 4. Install Ollama models (BLOCKED)              │
│     └─ Needs: Caleb to run ollama pull             │
│  ⏸️  5. Install systemd service (pending)           │
│  ⏸️  6. Configure cron (pending)                    │
│  ⏸️  7. Test cycle (pending)                        │
│  ⏸️  8. Update dashboard (pending)                  │
│                                                     │
│  [View Step 4 Details]                              │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Step Detail View

```
┌─────────────────────────────────────────────────────┐
│  Step 4: Install Ollama Models           [Back]     │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Status: 🔴 BLOCKED                                 │
│                                                     │
│  Description:                                       │
│  Pull qwen2.5:7b and llava:13b for Helios          │
│                                                     │
│  Blocked Reason:                                    │
│  Needs sudo access for ollama pull                 │
│                                                     │
│  Input Needed From: Caleb                          │
│                                                     │
│  Request:                                           │
│  Please run:                                       │
│  ollama pull qwen2.5:7b                           │
│  ollama pull llava:13b                            │
│                                                     │
│  [Mark Complete]  [Request Help]                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Agent Task View

```
┌─────────────────────────────────────────────────────┐
│  CHAD_YI - Current Tasks                            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  A6-4: Install Helios Service                       │
│  Progress: ████████░░░░ 38%                        │
│  └─ Step 4/8: Blocked on Ollama models             │
│                                                     │
│  A6-5: Dashboard Integration                        │
│  Progress: ░░░░░░░░░░░░ 0%                         │
│  └─ Not started (waiting on A6-4)                  │
│                                                     │
│  A1-5: Book flight to Japan                        │
│  Progress: ████████████ 100% ✅                    │
│  └─ Completed yesterday                            │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## AGENT PLANNING TEMPLATE

### When Agent Receives Task:

**Step 1: Analyze Task**
```
Task: "Install Helios COO Service"
Questions:
- What does this actually require?
- What are the sub-steps?
- What order do they go in?
- What dependencies exist?
- How long will each take?
- What could go wrong?
- What input might I need?
```

**Step 2: Create Plan**
```yaml
# agents/[name]/inbox/[task-id]-plan.yaml

task_id: "A6-4"
title: "Install Helios COO Service"

total_estimated_hours: 4

dependencies:
  external: ["Ollama installed", "sudo access"]
  internal: []

risks:
  - "Ollama models large (9GB), slow download"
  - "systemd might need restart"
  - "Port conflicts with other services"

steps:
  - id: 1
    title: "Create service file"
    description: "..."
    hours: 0.5
    done_definition: "helios.service exists and valid"
    
  - id: 2
    title: "Create audit script"
    description: "..."
    hours: 1.0
    done_definition: "Script runs without errors"
    
  - id: 3
    title: "Test audit script"
    description: "..."
    hours: 0.5
    done_definition: "All checks pass"
    
  - id: 4
    title: "Install Ollama models"
    description: "..."
    hours: 1.0
    may_need_input: true
    input_from: "Caleb"
    input_description: "Run ollama pull commands"
    
  # ... etc
```

**Step 3: Submit Plan**
```
Agent writes plan to outbox/[task-id]-plan.yaml
CHAD_YI reviews plan
CHAD_YI updates DATA/data.json with plan
Dashboard shows: "Task A6-4: 8 steps planned"
```

**Step 4: Execute Steps**
```
For each step:
  1. Update status: "starting"
  2. Do the work
  3. Verify done_definition met
  4. Update status: "done"
  5. Report to outbox/
  6. CHAD_YI updates DATA/
  7. Dashboard shows progress
```

---

## INTEGRATION WITH ARCHITECTURE

### CHAD_YI Task Planning:

When you assign me a task:
1. **I create plan** - Break into subtasks
2. **You review** (if complex) or trust me (if straightforward)
3. **I update DATA/** - Add plan to task
4. **Dashboard shows** - Progress bar, steps
5. **I execute** - Mark steps done
6. **Blocked?** - Request input, show in dashboard
7. **Complete** - All steps done

### Agent Task Planning:

When I assign task to agent:
1. **Agent creates plan** - Submits to outbox/
2. **I review plan** - Approve or adjust
3. **Update DATA/** - Add plan to task
4. **Agent executes** - Reports step progress
5. **Helios monitors** - Checks progress
6. **Dashboard shows** - Agent progress

### Dashboard Integration:

```javascript
// dashboard/js/task-detail.js

function renderTaskPlan(task) {
  const plan = task.plan;
  const progress = (plan.completed_steps / plan.total_steps) * 100;
  
  return `
    <div class="task-plan">
      <div class="progress-bar">
        <div class="progress-fill" style="width: ${progress}%"></div>
      </div>
      <div class="progress-text">
        ${plan.completed_steps} of ${plan.total_steps} steps (${Math.round(progress)}%)
      </div>
      
      <div class="steps-list">
        ${plan.steps.map(step => renderStep(step)).join('')}
      </div>
    </div>
  `;
}

function renderStep(step) {
  const statusIcon = {
    'done': '✅',
    'active': '🔄',
    'blocked': '🔴',
    'pending': '⏸️'
  };
  
  return `
    <div class="step ${step.status}">
      <span class="step-icon">${statusIcon[step.status]}</span>
      <span class="step-title">${step.id}. ${step.title}</span>
      ${step.status === 'blocked' ? `
        <div class="blocker">
          Blocked: ${step.blocked_reason}
          ${step.needs_input_from ? `<br>Needs: ${step.needs_input_from}` : ''}
        </div>
      ` : ''}
    </div>
  `;
}
```

---

## VERIFICATION

### Can Dashboard Support This?
**YES**
- Plan stored in task object
- JavaScript renders progress bar
- Steps list with status icons
- Blocked steps show reason

### Can Agents Use This?
**YES**
- Agent creates plan YAML
- Submits to outbox/
- I approve/update DATA/
- Agent reports step progress

### Can I Use This?
**YES**
- I break my tasks into steps
- Update plan as I go
- Dashboard shows progress
- You see blocked items

---

## IMPLEMENTATION

### Add to Current Build:

**1. Update DATA Schema (15 min)**
```json
{
  "tasks": {
    "[id]": {
      "...existing fields...",
      "plan": {
        "total_steps": 8,
        "completed_steps": 3,
        "estimated_hours": 4,
        "actual_hours": 2.5,
        "steps": [...]
      }
    }
  }
}
```

**2. Dashboard UI (1 hour)**
- Add progress bar
- Add steps list
- Add blocked reason display
- Add step detail modal

**3. Planning Template (30 min)**
- Create agents/_templates/task-plan.yaml
- Document planning process

---

## SUMMARY

**Task Planning System:**
- Tasks broken into steps
- Progress tracking
- Blocked items visible
- Time estimates
- Dependencies
- Dashboard integration

**Works for:**
- Me (CHAD_YI)
- All agents
- Complex multi-step tasks

**Shows on dashboard:**
- Progress bars
- Step lists
- Blocked reasons
- Time tracking

**Ready to build this + Phase 2 (Helios)?**