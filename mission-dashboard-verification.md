# MISSION DASHBOARD - VERIFICATION & TESTING

## AUTOMATED TESTING CHECKLIST

### FOUNDATION (Tasks 1-5)
- [ ] **Task 1: data.json loads** - Check if fetch('data.json') returns valid JSON
- [ ] **Task 2: Stats update** - Verify stat values change when data changes
- [ ] **Task 3: Workflow counts** - Check pipeline numbers match data
- [ ] **Task 4: Project progress** - Verify % calculates from done/total
- [ ] **Task 5: Auto-refresh** - Confirm data reloads every 30s

### TASK MANAGEMENT (Tasks 6-12)
- [ ] **Task 6: Add Task** - Modal opens, form submits, task appears in data
- [ ] **Task 7: Edit Task** - Click task opens edit modal, changes save
- [ ] **Task 8: Complete Task** - Check off moves task to Done, updates stats
- [ ] **Task 9: Delete Task** - Delete button removes task with confirmation
- [ ] **Task 10: Task Detail** - Click shows full task info
- [ ] **Task 11: Filters** - Filter buttons show correct filtered tasks
- [ ] **Task 12: Search** - Search box filters tasks by text

### PROJECT MANAGEMENT (Tasks 13-16)
- [ ] **Task 13: Project Detail** - Click project shows modal with stats
- [ ] **Task 14: Project Tasks** - All tasks for project display correctly
- [ ] **Task 15: Timeline** - Milestone view renders
- [ ] **Task 16: Archive** - Archive button hides completed projects

### DIAGNOSTIC COMMANDS

**Test data.json loading:**
```javascript
fetch('data.json').then(r => r.json()).then(d => console.log('✅ Data loaded:', d.stats))
```

**Test localStorage persistence:**
```javascript
console.log('localStorage data:', localStorage.getItem('missionControlData'))
```

**Test task creation:**
```javascript
// Add test task
dashboardData.tasks.push({id: 'TEST', title: 'Test Task', project: 'A1', priority: 'high', status: 'pending'})
saveData()
// Check if it persists after refresh
```

## VERIFICATION CRON JOB

Need to create a cron job that:
1. Loads the dashboard URL
2. Runs JavaScript tests
3. Reports which features work/don't work
4. Alerts if something is broken
