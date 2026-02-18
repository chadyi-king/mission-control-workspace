# Mission Control Dashboard - Comprehensive Fix Plan
**For:** Helios (New Infrastructure Agent)  
**Date:** Feb 19, 2026  
**Priority:** URGENT  
**Approach:** Phased execution with audits, backups, and checkpoints

---

## 🎯 EXECUTION PHILOSOPHY

**Data First, Design Second**  
**Backup Before Every Change**  
**Audit After Every Phase**  
**Caleb Approval Required Between Phases**

---

## 📋 PRE-FLIGHT CHECKLIST (Before Starting)

```bash
# 1. Verify current data.json integrity
python3 -c "import json; d=json.load(open('data.json')); print(f'Tasks: {len(d[\"tasks\"])}'); print(f'Last Updated: {d[\"lastUpdated\"]}')"

# 2. Create full backup
cp data.json data-BACKUP-20260219-START.json

# 3. Create git branch
git checkout -b dashboard-fixes-phase1

# 4. Verify branch
git branch
```

---

## PHASE 1: DATA INTEGRITY & STRUCTURE (Days 1-2)

### 1.1 Data.json Structure Verification
**Task:** Ensure data.json has all required fields for new dashboard features

**Checklist:**
- [ ] Verify `agents` object has all 7 agents with correct status
- [ ] Verify `agentDetails` has expanded info for each agent
- [ ] Verify `workflow` arrays are accurate (pending/active/review/done)
- [ ] Verify `inputsNeeded` has real tasks requiring Caleb input
- [ ] Verify `urgentTaskDetails` has proper deadline calculations
- [ ] Add new field: `agentActivityLog` (last 5 activities per agent)
- [ ] Add new field: `taskRankings` (Caleb's custom priority order)

**New Data Structure to Add:**
```json
{
  "agentActivityLog": {
    "chad-yi": [
      {"time": "2026-02-19T04:30:00", "action": "Updated Quanta status", "task": "A5-1"},
      {"time": "2026-02-19T04:15:00", "action": "Fixed Redis communication", "task": "A6-14"}
    ],
    "escritor": [
      {"time": "2026-02-18T20:00:00", "action": "Completed Chapter 12 review", "task": "A2-13"}
    ]
  },
  "taskRankings": {
    "calebPriority": ["B6-3", "B6-6", "A1-2", "A1-5", "B6-8"]
  }
}
```

### 1.2 Document Storage Infrastructure
**Task:** Create proper file structure for Resources page

**Create Directory Structure:**
```
/resources/
  /projects/
    /A1-Personal/
      /tasks/
        /A1-1-Taiwan-Flights/
        /A1-2-Daily-Payments/
    /A2-REUNITE/
      /tasks/
        /A2-13-Chapter-13/
          /drafts/
          /research/
    /B6-Elluminate/
      /tasks/
        /B6-3-SPH-Items/
  /general/
```

**Checklist:**
- [ ] Create `/resources/` directory
- [ ] Create subdirectories for each project
- [ ] Create task subdirectories
- [ ] Create `resources-index.json` for tracking uploads
- [ ] Create upload handler script

### 1.3 Phase 1 Audit
**Task:** Verify data structure before proceeding

```bash
# Audit script
python3 -c "
import json
d = json.load(open('data.json'))
assert len(d['tasks']) == 82, 'Task count wrong'
assert 'agentActivityLog' in d, 'Missing agentActivityLog'
assert 'taskRankings' in d, 'Missing taskRankings'
print('✅ Phase 1 Audit: PASSED')
"
```

**Checkpoint:** WAIT FOR CALEB APPROVAL before Phase 2

---

## PHASE 2: HOMEPAGE DATA FIXES (Days 3-4)

### 2.1 Agent Activity Section
**File:** `index.html`

**Changes:**
- [ ] Fix "Chad-yi" → "CHAD_YI" (remove dash, capitalize)
- [ ] Replace timing display with clear label: "Last seen: 10h 38m ago"
- [ ] Add "Online" indicator logic: if lastActive < 15 min, show green dot
- [ ] Load agent data from `data.json.agents` dynamically
- [ ] Display current task from `agent.currentTask`
- [ ] Show project name from task lookup
- [ ] Add "Last 5 Activities" expandable section (use `agentActivityLog`)

### 2.2 Input Needed Section
**Changes:**
- [ ] Convert from columns to cards layout
- [ ] Each card shows: Task title, Project, Brief description
- [ ] Click to expand: Full description, what input is needed
- [ ] Load from `data.json.inputsNeeded` and `inputDetails`

### 2.3 System Online Bar
**Changes:**
- [ ] Show count of "active" agents only (not total)
- [ ] Replace "velocity" with useful stats (choose from options below)
- [ ] Add click-to-expand for agent list with statuses

**Statistic Options for Top Bar:**
```javascript
const topBarStats = [
  { label: "Active Agents", value: agents.filter(a => a.status === 'active').length },
  { label: "Tasks Due Today", value: tasks.filter(t => t.deadline === today).length },
  { label: "Overdue Tasks", value: tasks.filter(t => isOverdue(t)).length },
  { label: "Completed This Week", value: tasks.filter(t => completedThisWeek(t)).length },
  { label: "Token Usage", value: "Fetch from OpenClaw" },
  { label: "API Calls Today", value: "Fetch from logs" }
];
```

### 2.4 Phase 2 Audit
- [ ] Screenshot homepage before/after
- [ ] Verify agent names display correctly
- [ ] Verify Input Needed cards show real data
- [ ] Check System Online stats accuracy

**Checkpoint:** WAIT FOR CALEB APPROVAL before Phase 3

---

## PHASE 3: HOMEPAGE DESIGN & RANKING (Days 5-6)

### 3.1 System Health Grid Replacement
**Changes:**
- [ ] Replace "System Health" with 6-card grid (3x2)
- [ ] Use existing color scheme (red/blue/green/yellow)
- [ ] Card ideas:
  1. Active Agents (green)
  2. Tasks Due Today (red if >0)
  3. Completed This Week (blue)
  4. Overdue Tasks (red)
  5. Token Usage/Cost (yellow)
  6. API Calls (blue)

### 3.2 Task Ranking Table (New Feature)
**Changes:**
- [ ] Add full-height column on right side (spans rows 1-2)
- [ ] Title: "Caleb's Priority Tasks"
- [ ] Drag-and-drop reordering (use HTML5 drag API)
- [ ] Auto-sort: Urgent first, then deadline, then custom order
- [ ] Save order to `data.json.taskRankings.calebPriority`
- [ ] Read order when displaying

### 3.3 This Week Calendar Improvements
**Changes:**
- [ ] Color-code by urgency:
  - Red: Missed deadline
  - Orange: Due today
  - Yellow: Due this week
  - Green: Future
- [ ] Sort by urgency (not just date)
- [ ] Add scroll if many tasks

### 3.4 Phase 3 Audit
- [ ] Test drag-and-drop functionality
- [ ] Verify color coding works
- [ ] Screenshot full homepage

**Checkpoint:** WAIT FOR CALEB APPROVAL before Phase 4

---

## PHASE 4: CATEGORIES PAGE (Days 7-8)

### 4.1 Statistics Overhaul
**File:** `categories.html`

**Changes:**
- [ ] Replace 6 stats with up to 12 compact stats
- [ ] Calculate from real data.json:
  - Total Tasks
  - Pending
  - Active
  - Done This Week
  - Deadline Today
  - Deadline This Week
  - Urgent
  - High Priority
  - Overdue
  - Completed Rate
  - Active Agents
  - Blocked Agents

### 4.2 Filter System Fix
**Changes:**
- [ ] Fix all broken filters (only ID/name works currently)
- [ ] Add filters:
  - By Status (pending/active/review/done)
  - By Priority (high/medium/low)
  - By Agent
  - By Deadline (today/this week/overdue)
- [ ] Keep Project ID as default sort
- [ ] Ensure numerical ordering (A1, A2... not A1, B1, C1)

### 4.3 Project Cards Improvements
**Changes:**
- [ ] Fix "undefined" tags
- [ ] Only show tags that exist (urgent, deadline, high priority)
- [ ] Color-code tags: Urgent=red, Deadline=orange, High=yellow
- [ ] Fix "complete portion" statistics

### 4.4 Project Modal Fixes
**Changes:**
- [ ] Fix scroll when >7 tasks
- [ ] Better task descriptions
- [ ] Remove "Spawn Agent" button
- [ ] Remove "Add Task" button
- [ ] Keep "Open Project" button (this works)

### 4.5 Phase 4 Audit
- [ ] Test all filters
- [ ] Verify project cards show correct data
- [ ] Test modal with many tasks

**Checkpoint:** WAIT FOR CALEB APPROVAL before Phase 5

---

## PHASE 5: SYSTEM PAGE RESTRUCTURE (Days 9-11)

### 5.1 Organizational Structure Redesign
**File:** `system.html`

**Hierarchy to Display:**
```
Caleb (CEO) - You
  ↓
CHAD_YI (Brain / Orchestrator)
  ↓
Helios (COO / Spine)
  ↓
  ├─ Escritor (Writer) → A2-13
  ├─ Quanta (Trading) → A5-1
  ├─ Forger (Builder) → B6
  ├─ MensaMusa (Options) → A5-2 (blocked)
  └─ Autour (Content) → A3 (not spawned)
```

**Changes:**
- [ ] Visual hierarchy showing reporting structure
- [ ] Each agent clickable
- [ ] Show: Role, Current Project, Current Task, Status
- [ ] Show collaboration links (who works with whom)
- [ ] Last 5 activities per agent
- [ ] Action needed indicator

### 5.2 Agent Roster Integration
**Changes:**
- [ ] Combine with organizational structure
- [ ] Expandable agent profiles
- [ ] Show: Agent name, Role, Status, Current Task, Last Activity
- [ ] Collaboration matrix (which agents work together)

### 5.3 System Status Replacement
**Changes:**
- [ ] Replace placeholder stats with OpenClaw-style metrics:
  - Models used today
  - Total tokens consumed
  - Estimated cost
  - API calls per agent
  - Session duration
  - Skills utilized

### 5.4 Skill Recommendations
**Changes:**
- [ ] Show skills each agent has
- [ ] Suggest skills based on agent's tasks
- [ ] Research new skills that could help

### 5.5 Phase 5 Audit
- [ ] Verify hierarchy displays correctly
- [ ] Check all agent data loads from data.json
- [ ] Test agent profile expansion

**Checkpoint:** WAIT FOR CALEB APPROVAL before Phase 6

---

## PHASE 6: RESOURCES PAGE (Days 12-13)

### 6.1 Upload System Restructure
**File:** `resources.html`

**Changes:**
- [ ] Remove 5 separate upload places
- [ ] Create single unified upload interface
- [ ] Project selector dropdown
- [ ] Task selector dropdown (filtered by project)
- [ ] Drag-and-drop file upload
- [ ] Files stored in `/resources/projects/{project}/{task}/`

### 6.2 Document Index
**Changes:**
- [ ] Create `resources-index.json`:
```json
{
  "uploads": [
    {
      "id": "upload-001",
      "filename": "chapter13-draft.docx",
      "project": "A2",
      "task": "A2-14",
      "uploadedAt": "2026-02-19T10:00:00",
      "uploadedBy": "Caleb",
      "agent": "Escritor"
    }
  ]
}
```

### 6.3 Recent Uploads
**Changes:**
- [ ] Display recent uploads list
- [ ] Filter by project/task
- [ ] Click to download/view

### 6.4 Agent Needs
**Changes:**
- [ ] Keep current "What each agent needs" section
- [ ] Ensure links work correctly
- [ ] Show document status (uploaded/pending)

### 6.5 Phase 6 Audit
- [ ] Test upload flow
- [ ] Verify files save to correct folders
- [ ] Check agent needs links

**Checkpoint:** WAIT FOR CALEB APPROVAL before Phase 7

---

## PHASE 7: FINAL INTEGRATION & TESTING (Days 14-15)

### 7.1 Cross-Page Consistency
**Changes:**
- [ ] Ensure all pages use same data.json structure
- [ ] Verify agent names consistent (CHAD_YI not Chad-yi)
- [ ] Check color schemes match
- [ ] Verify navigation works between pages

### 7.2 Performance Optimization
**Changes:**
- [ ] Minimize data.json reads (cache in JS)
- [ ] Lazy load expandable sections
- [ ] Optimize images/assets
- [ ] Ensure <3 second load time

### 7.3 Mobile Responsiveness
**Changes:**
- [ ] Test on mobile devices
- [ ] Ensure drag-and-drop works on touch
- [ ] Check layout doesn't break

### 7.4 Final Audit
**Complete Checklist:**
- [ ] Homepage all features work
- [ ] Categories all filters work
- [ ] System page shows hierarchy
- [ ] Resources upload works
- [ ] All data loads from data.json
- [ ] No hardcoded placeholder data
- [ ] All agent statuses accurate

### 7.5 Deployment
**Steps:**
```bash
# 1. Merge to main
git checkout main
git merge dashboard-fixes-phase6

# 2. Push to deploy
git push origin main

# 3. Verify Render deployment
curl https://mission-control-dashboard-hf0r.onrender.com/health

# 4. Test live site
# Take screenshots of all pages
# Verify all features work
```

---

## 🚨 BACKUP PROTOCOL (Every Phase)

**Before Starting Each Phase:**
```bash
# Create timestamped backup
cp data.json data-BACKUP-$(date +%Y%m%d-%H%M%S).json

# Create git checkpoint
git add .
git commit -m "Checkpoint: Before Phase X"
```

**If Something Breaks:**
```bash
# Restore from backup
cp data-BACKUP-XXXX.json data.json

# Or restore from git
git checkout HEAD -- data.json

# Rollback entire phase
git reset --hard HEAD~1
```

---

## 📊 PROGRESS TRACKING

**Update this after each phase:**

| Phase | Status | Caleb Approved | Date Completed |
|-------|--------|----------------|----------------|
| 1: Data Structure | ⬜ Not Started | ⬜ | - |
| 2: Homepage Data | ⬜ Not Started | ⬜ | - |
| 3: Homepage Design | ⬜ Not Started | ⬜ | - |
| 4: Categories | ⬜ Not Started | ⬜ | - |
| 5: System | ⬜ Not Started | ⬜ | - |
| 6: Resources | ⬜ Not Started | ⬜ | - |
| 7: Integration | ⬜ Not Started | ⬜ | - |

---

## 🔄 COMMUNICATION PROTOCOL

**After Each Phase:**
1. Send Caleb: "Phase X Complete"
2. Attach: Screenshots of changes
3. Provide: Summary of what was changed
4. Wait for: "Approved - proceed to Phase X+1"

**If Blocked:**
1. Document the issue
2. Send Caleb: "Blocked on Phase X: [description]"
3. Wait for: Guidance before proceeding

---

## ✅ SUCCESS CRITERIA

**Dashboard is "Done" when:**
- [ ] All 4 pages load without errors
- [ ] All data comes from data.json (no placeholders)
- [ ] Agent statuses match reality
- [ ] Caleb can upload documents by project/task
- [ ] Task ranking drag-and-drop works
- [ ] All filters work on Categories page
- [ ] System page shows real hierarchy
- [ ] Caleb approves all changes

---

**Estimated Total Time:** 15 days  
**Checkpoints:** 7 (between each phase)  
**Risk Level:** Medium (mitigated by backups and audits)

**Start when Caleb approves this plan.**
