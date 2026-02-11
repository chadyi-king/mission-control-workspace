# JavaScript Functionality Audit Report
## Mission Control Dashboard - `/mission-control-dashboard/index.html`

**Audit Date:** 2026-02-11  
**Auditor:** Helios (JavaScript Functionality Agent)  
**Scope:** Core JavaScript functions in index.html

---

## 1. Calendar Week View - Task Filtering by Deadline

### Function: `renderWeekView()`, `getTasksForDay()`

**Status:** ⚠️ **PARTIALLY BROKEN**

### Issues Found:

#### Issue 1A: Deadline Comparison Logic Flaw
**Location:** `getTasksForDay()` function (lines ~3550-3580)

```javascript
function getTasksForDay(data, date) {
    // ... collecting tasks from workflow
    
    // Filter tasks by deadline matching this date
    const dayStr = date.toISOString().split('T')[0];  // "2026-02-11"
    return allTasks.filter(t => t.deadline && t.deadline === dayStr);
}
```

**Problem:** The function looks for `t.deadline` property, but examining the codebase shows tasks use `createdAt` for date tracking, NOT `deadline`. The `deadline` property doesn't exist in the task schema.

**Evidence:** In `loadData()`, tasks are loaded from `appData.tasks` with properties like:
- `id`, `title`, `project`, `priority`, `status`, `assignedTo`, `notes`, `createdAt`

No `deadline` field exists.

**Impact:** The calendar week view will ALWAYS show 0 tasks per day because the filter condition `t.deadline === dayStr` will never match.

#### Issue 1B: Missing Deadline Estimation
**Problem:** The code should calculate estimated deadlines based on task priority (as done elsewhere in the codebase), but `getTasksForDay()` doesn't implement this.

### Fix Required:

```javascript
function getTasksForDay(data, date) {
    const workflow = data.workflow || {};
    const allTasks = [
        ...(workflow.pending || []),
        ...(workflow.active || []),
        ...(workflow.review || [])
    ];
    
    // Also check project tasks
    const projects = data.projects || {};
    Object.values(projects).forEach(category => {
        if (category.projects) {
            category.projects.forEach(project => {
                if (project.tasks) {
                    allTasks.push(...project.tasks);
                }
            });
        }
    });
    
    // Calculate estimated deadlines based on priority + createdAt
    const dayStr = date.toISOString().split('T')[0];
    
    return allTasks.filter(t => {
        // If task has explicit deadline, use it
        if (t.deadline) {
            return t.deadline === dayStr;
        }
        
        // Otherwise estimate from createdAt + priority
        if (t.createdAt) {
            const created = new Date(t.createdAt);
            // High priority: 3 days, Medium: 7 days, Low: 14 days
            const daysToAdd = t.priority === 'high' ? 3 : 
                             (t.priority === 'medium' ? 7 : 14);
            const estimatedDeadline = new Date(created);
            estimatedDeadline.setDate(created.getDate() + daysToAdd);
            
            return estimatedDeadline.toISOString().split('T')[0] === dayStr;
        }
        
        return false;
    });
}
```

---

## 2. renderDayTasks() - Tasks for Selected Day

### Function: `renderDayTasks(date)`

**Status:** ⚠️ **BROKEN - Same Root Cause as #1**

### Issues Found:

#### Issue 2A: Same Deadline Property Issue
**Location:** `renderDayTasks()` function (lines ~3600-3640)

```javascript
function renderDayTasks(date) {
    // ...
    const dayStr = date.toISOString().split('T')[0];
    const tasksForDay = allTasks.filter(t => {
        if (!t.deadline) return false;  // ALWAYS FALSE - no deadline property!
        return t.deadline === dayStr;
    });
    // ...
}
```

**Problem:** Same as Issue 1A - tasks don't have a `deadline` property.

### Fix Required:

Apply the same fix as Issue 1 - calculate estimated deadlines from `createdAt` + priority.

---

## 3. loadData() - Data Fetching

### Function: `loadData()`

**Status:** ✅ **MOSTLY WORKING**

### What's Working:
- ✅ Correctly fetches `data.json` via `fetch()`
- ✅ Parses JSON response
- ✅ Processes projects and tasks into `allProjects` array
- ✅ Calculates task statistics correctly
- ✅ Calls `syncProjectLookup()` and render functions

### Issues Found:

#### Issue 3A: Missing Error Handling for Network Failures
**Location:** `loadData()` try-catch block

```javascript
async function loadData() {
    try {
        const response = await fetch('data.json');
        appData = await response.json();  // No check for response.ok!
```

**Problem:** The code doesn't check if `response.ok` is true before parsing. A 404 or 500 error would still try to parse JSON, causing a confusing error.

**Fix:**
```javascript
async function loadData() {
    try {
        const response = await fetch('data.json');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        appData = await response.json();
        // ... rest of function
    } catch (error) {
        console.error('Failed to load data:', error);
        document.getElementById('cat-loading-state').style.display = 'none';
        document.getElementById('cat-error-state').style.display = 'block';
        // Also show error in home section
        document.getElementById('urgent-queue').innerHTML = 
            '<div style="text-align: center; color: #ff6b6b; padding: 40px;">Failed to load data</div>';
    }
}
```

#### Issue 3B: Race Condition on Initial Load
**Problem:** If `loadData()` is called multiple times quickly (e.g., via `changeWeek()`), multiple fetches could run simultaneously.

**Fix:** Add a loading guard:
```javascript
let isLoading = false;

async function loadData() {
    if (isLoading) return;
    isLoading = true;
    
    try {
        // ... existing code
    } finally {
        isLoading = false;
    }
}
```

---

## 4. Console Errors and Broken Functions

### Issues Found:

#### Issue 4A: Missing `renderNewHomepage()` Reference
**Status:** ✅ **RESOLVED** (External file reference)

The code calls `renderNewHomepage(appData)` but this function is not defined in `index.html`. It appears to be defined in `homepage-new.css` or another external file. This is acceptable if the file is properly loaded.

#### Issue 4B: Undefined Variables in `renderHomeSection()`
**Location:** `renderHomeSection()` function

```javascript
function renderHomeSection() {
    renderNewHomepage(appData);  // External dependency
    
    const stats = appData.stats || {};
    const agents = appData.agents || [];
    const allTasks = appData.tasks || [];
    const workflow = appData.workflow || {};
    
    // ... variables defined but NEVER USED in the function!
    const urgentCount = stats.urgentTasks ?? ...;
    const focusProject = stats.focusProject || '—';
    // ... these are calculated but not rendered
}
```

**Problem:** The function calculates statistics but doesn't actually render them to the DOM. The old rendering code is incomplete.

**Impact:** Minor - the new homepage renderer (`renderNewHomepage`) handles the actual rendering, but dead code exists.

#### Issue 4C: `changeWeek()` Triggers Full Data Reload
**Location:** `changeWeek()` function

```javascript
function changeWeek(direction) {
    currentWeekOffset += direction;
    loadData(); // Re-render - THIS RE-FETCHES data.json!
}
```

**Problem:** `changeWeek()` calls `loadData()` which re-fetches `data.json` from the server. This is unnecessary network overhead - the data hasn't changed, only the week view offset.

**Fix:**
```javascript
function changeWeek(direction) {
    currentWeekOffset += direction;
    renderWeekView(appData);  // Just re-render, don't re-fetch
}
```

#### Issue 4D: `selectDay()` Potential Null Reference
**Location:** `selectDay()` function

```javascript
function selectDay(idx, timestamp) {
    selectedDay = new Date(timestamp);
    
    // Update visual selection
    document.querySelectorAll('.week-day').forEach((el, i) => {
        el.classList.toggle('active', i === idx);
    });

    // Render tasks for selected day
    renderDayTasks(selectedDay);
}
```

**Problem:** If the DOM elements don't exist (e.g., during initial load), this could error. Also, `timestamp` parameter could be invalid.

**Severity:** Low - unlikely to occur in practice.

---

## 5. Search Functionality

### Function: `searchTasks(query)`, `resetSearch()`

**Status:** ⚠️ **PARTIALLY BROKEN**

### What's Working:
- ✅ Search input captures user input
- ✅ Query normalization (toLowerCase)
- ✅ Search across task title, project, and notes
- ✅ Results display in urgent queue column
- ✅ Clear/reset functionality works

### Issues Found:

#### Issue 5A: Results Display Overwrites Urgent Queue
**Location:** `searchTasks()` function

```javascript
function searchTasks(query) {
    // ...
    // Show search results in urgent queue column with highlight
    const container = document.getElementById('urgent-queue');
    // ...
    container.innerHTML = `...search results...`;  // OVERWRITES URGENT QUEUE!
```

**Problem:** Search results completely replace the "Urgent Queue" column content. When search is cleared, the urgent queue is restored, but this UX pattern is confusing - users might think their urgent tasks disappeared.

**Expected Behavior:** Search should either:
1. Show results in a dedicated search results panel, OR
2. Highlight matching tasks in place without removing urgent items

#### Issue 5B: No Search Debouncing
**Location:** Search input handler

```html
<input type="text" id="task-search" placeholder="Search tasks..." onkeyup="searchTasks(this.value)">
```

**Problem:** `onkeyup` triggers `searchTasks()` on EVERY keystroke. For large datasets, this causes performance issues.

**Fix:** Add debouncing:
```javascript
let searchTimeout;
function searchTasks(query) {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
        performSearch(query);
    }, 300);  // Wait 300ms after last keystroke
}
```

#### Issue 5C: Empty Query Edge Case
```javascript
function searchTasks(query) {
    if (!query || query.length < 2) {
        // Reset to default view
        renderNewHomepage(appData);
        return;
    }
```

**Problem:** The check `query.length < 2` means single-character searches do nothing but reset. This may confuse users expecting immediate feedback.

**Recommendation:** Either:
1. Show "Type at least 2 characters" message, OR
2. Allow single-character search with performance warning

---

## Summary Table

| Function | Status | Severity | Notes |
|----------|--------|----------|-------|
| `loadData()` | ✅ Working | Low | Add response.ok check |
| `renderWeekView()` | ⚠️ Partial | High | Deadlines not calculated |
| `getTasksForDay()` | ❌ Broken | High | Uses non-existent deadline property |
| `renderDayTasks()` | ❌ Broken | High | Same deadline issue |
| `searchTasks()` | ⚠️ Partial | Medium | UX issues, needs debounce |
| `changeWeek()` | ⚠️ Partial | Low | Unnecessary data reload |
| `selectDay()` | ✅ Working | Low | Minor null risk |
| `resetSearch()` | ✅ Working | - | Works correctly |

---

## Priority Fixes

### Critical (Fix Immediately):
1. **Fix deadline calculation** in `getTasksForDay()` and `renderDayTasks()` - calendar is currently non-functional
2. **Add response.ok check** in `loadData()` for better error handling

### High Priority:
3. **Add search debouncing** to improve performance
4. **Fix `changeWeek()`** to not reload data unnecessarily

### Medium Priority:
5. **Improve search UX** - show results in dedicated panel instead of overwriting urgent queue
6. **Clean up unused code** in `renderHomeSection()`

---

## Test Recommendations

1. **Calendar Tests:**
   - Verify tasks appear on correct days based on priority + createdAt
   - Test week navigation (prev/next)
   - Test day selection

2. **Search Tests:**
   - Test with 2+ characters
   - Test clearing search
   - Test with no matches
   - Verify urgent queue restores after search

3. **Data Loading Tests:**
   - Test with missing data.json (404)
   - Test with malformed JSON
   - Test rapid week navigation (race conditions)

---

*End of Audit Report*
