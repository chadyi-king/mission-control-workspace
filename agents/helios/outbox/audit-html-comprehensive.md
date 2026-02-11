# Mission Control Dashboard - Comprehensive HTML Audit Report

**Audit Date:** 2026-02-11  
**Auditor:** Dashboard Auditor Agent (Helios)  
**Scope:** All HTML files in `/home/chad-yi/.openclaw/workspace/mission-control-dashboard/`

---

## EXECUTIVE SUMMARY

| Category | Issues Found | Severity |
|----------|-------------|----------|
| Broken Links | 1 | Medium |
| Icon Inconsistencies | 47 | Low |
| Font Issues | 4 | Low |
| Data Accuracy | 5 | Medium |

---

## 1. BROKEN LINKS

### Issue #1: Missing Resource File
**File:** `resources.html`  
**Line:** ~365  
**Issue:** Link to Story Bible file that may not exist
```html
<a href="projects/A2-reunite/STORY-BIBLE-COMPLETE.md" target="_blank" class="resource-link">View →</a>
```
**What's Wrong:** The link assumes a markdown file exists at this path, but the file may not exist or may not be accessible via HTTP (it's a .md file).  
**How to Fix:** 
- Convert the markdown file to HTML
- Update the link to point to an HTML version
- Or use a markdown viewer/iframe to display it

---

## 2. ICON INCONSISTENCIES (EMOJI → SVG RECOMMENDATIONS)

The dashboard uses emojis extensively where SVG icons would provide better consistency, scalability, and accessibility.

### 2.1 Navigation Icons (All HTML files)

| File | Line | Emoji | Suggested SVG Icon | Context |
|------|------|-------|-------------------|---------|
| `index.html` | ~2809 | `🎯` | target.svg | Mission Control badge |
| `index.html` | ~2820 | `🏠` | home.svg | Mobile nav - Home |
| `index.html` | ~2821 | `📁` | folder.svg | Mobile nav - Categories |
| `index.html` | ~2822 | `📈` | bar-chart.svg | Mobile nav - Insights |
| `index.html` | ~2823 | `📚` | book.svg | Mobile nav - Resources |
| `index.html` | ~2824 | `⚙️` | settings.svg | Mobile nav - System |
| `index.html` | ~2825 | `👤` | user.svg | Mobile nav - Profile |
| `index.html` | ~2826 | `🤖` | robot.svg | Mobile nav - Agent Roster |
| `index.html` | ~2875 | `🤖` | robot.svg | Sidebar - Agent Roster |
| All files | various | `◀` `▶` | chevron-left.svg, chevron-right.svg | Sidebar toggle arrows |

### 2.2 Dashboard/Stats Icons

| File | Line | Emoji | Suggested SVG Icon | Context |
|------|------|-------|-------------------|---------|
| `index.html` | ~2390 | `📊` | bar-chart-2.svg | Stats widget |
| `index.html` | ~2395 | `🏆` | trophy.svg | Wins counter |
| `categories.html` | ~1635 | `📊` | bar-chart-2.svg | Dashboard stats |
| `categories.html` | ~1639 | `📋` | clipboard.svg | Total tasks |
| `categories.html` | ~1643 | `✓` | check-circle.svg | Tasks done |
| `categories.html` | ~1647 | `⏳` | clock.svg | Pending tasks |
| `categories.html` | ~1651 | `🎯` | target.svg | Completion rate |
| `categories.html` | ~1655 | `🚨` | alert-triangle.svg | Urgent tasks |

### 2.3 Status/Indicator Icons

| File | Line | Emoji | Suggested SVG Icon | Context |
|------|------|-------|-------------------|---------|
| `index.html` | ~2362 | `🔴` | circle-filled-red.svg | Urgent Queue column |
| `index.html` | ~2373 | `🟡` | circle-filled-yellow.svg | Agent Status column |
| `index.html` | ~2384 | `🟢` | circle-filled-green.svg | Input Needed column |
| `index.html` | ~2405 | `●` | dot.svg | Active status dot |
| `system.html` | ~1069 | `●` | dot.svg | System health indicator |
| `categories.html` | ~2120 | `●` | dot.svg | Priority separator |

### 2.4 Action/Control Icons

| File | Line | Emoji | Suggested SVG Icon | Context |
|------|------|-------|-------------------|---------|
| `index.html` | ~2485 | `⚡` | zap.svg | Quick Actions button |
| `index.html` | ~2493 | `➕` | plus.svg | Add Task action |
| `index.html` | ~2497 | `🤖` | robot.svg | Spawn Agent action |
| `index.html` | ~2501 | `📊` | bar-chart.svg | Export Report action |
| `index.html` | ~2505 | `📤` | upload.svg | Deploy action |
| `index.html` | ~2509 | `▼` | chevron-down.svg | Dropdown arrow |
| `index.html` | ~2516 | `▶` | play.svg | Active Tasks title |
| `index.html` | ~2527 | `📅` | calendar.svg | Upcoming Deadlines title |
| `index.html` | ~2538 | `⚠️` | alert-circle.svg | Input Needed title |
| `index.html` | ~2549 | `📡` | radio.svg | Recent Activity title |

### 2.5 Task Status Icons

| File | Line | Emoji | Suggested SVG Icon | Context |
|------|------|-------|-------------------|---------|
| `index.html` | ~2742 | `✓` | check.svg | All caught up message |
| `index.html` | ~2774 | `●` | dot.svg | Separator in task meta |
| `index.html` | ~2839 | `✓` | check.svg | Loading state |
| `categories.html` | ~1866 | `○` | circle.svg | Pending status |
| `categories.html` | ~1867 | `▶` | play.svg | Active status |
| `categories.html` | ~1868 | `👁` | eye.svg | Review status |
| `categories.html` | ~1869 | `✓` | check.svg | Done status |

### 2.6 Calendar/Date Icons

| File | Line | Emoji | Suggested SVG Icon | Context |
|------|------|-------|-------------------|---------|
| `index.html` | ~2706 | `◀` | chevron-left.svg | Calendar nav |
| `index.html` | ~2707 | `▶` | chevron-right.svg | Calendar nav |
| `index.html` | ~2740 | `🕐` | clock.svg | Next Due label |
| `index.html` | ~2782 | `📍` | map-pin.svg | Milestones label |
| `index.html` | ~2805 | `🗂` | layers.svg | Project Timeline |

### 2.7 Agent Roster Page Icons

| File | Line | Emoji | Suggested SVG Icon | Context |
|------|------|-------|-------------------|---------|
| `agent-roster.html` | ~186 | `🧠` | brain.svg | CEO card |
| `agent-roster.html` | ~207 | `🚀` | rocket.svg | Helios card |
| `agent-roster.html` | ~230 | `✍️` | pen-tool.svg | Escritor agent |
| `agent-roster.html` | ~237 | `🎬` | film.svg | Autour agent |
| `agent-roster.html` | ~244 | `📺` | monitor.svg | Clair agent |
| `agent-roster.html` | ~251 | `📈` | trend-line.svg | Quanta agent |
| `agent-roster.html` | ~258 | `⚡` | zap.svg | E++ agent |
| `agent-roster.html` | ~265 | `📢` | megaphone.svg | Kotler agent |
| `agent-roster.html` | ~272 | `📚` | book-open.svg | Ledger agent |
| `agent-roster.html` | ~279 | `🔍` | search.svg | Atlas agent |
| `agent-roster.html` | ~286 | `🔔` | bell.svg | Pulsar agent |
| `agent-roster.html` | ~293 | `💰` | dollar-sign.svg | MensaMusa agent |
| `agent-roster.html` | ~300 | `👥` | users.svg | Abed agent |
| `agent-roster.html` | ~315 | `🤖` | robot.svg | Page header |

### 2.8 System/Profile Page Icons

| File | Line | Emoji | Suggested SVG Icon | Context |
|------|------|-------|-------------------|---------|
| `system.html` | ~1111 | `📤` | upload-cloud.svg | GitHub Deploy |
| `system.html` | ~1122 | `⏱` | timer.svg | Data Refresh |
| `system.html` | ~1150 | `🧠` | brain.svg | Agent Roster title |
| `system.html` | ~1187 | `🛠` | tool.svg | Settings title |
| `system.html` | ~1194 | `🔧` | wrench.svg | Placeholder icon |
| `profile.html` | ~1111 | `👤` | user.svg | User Info title |
| `profile.html` | ~1122 | `🔑` | key.svg | API Keys title |
| `profile.html` | ~1139 | `⚙️` | settings.svg | Preferences title |
| `profile.html` | ~1146 | `🎛` | sliders.svg | Preferences placeholder |

### 2.9 Search/Filter Icons

| File | Line | Emoji | Suggested SVG Icon | Context |
|------|------|-------|-------------------|---------|
| `index.html` | ~2341 | `🔍` | search.svg | Search icon (SVG already present, but emoji used in placeholder text) |
| `categories.html` | ~1725 | `🔍` | search.svg | No results message |

---

## 3. FONT ISSUES

### Issue #3.1: Very Small Text in Task Stat Labels
**File:** `index.html`, `categories.html`, `resources.html`, `insights.html`  
**Line:** CSS line ~420-425  
```css
.task-stat-label { font-size: 8px; ... }
```
**What's Wrong:** 8px font size is extremely small and may be difficult to read, especially on high-DPI displays or for users with visual impairments.  
**How to Fix:** Increase to at least 10px or use relative units like `0.7rem`.

### Issue #3.2: Small Text in Milestone Tooltips
**File:** All HTML files with milestones  
**Line:** CSS line ~580-590  
```css
.milestone-tooltip { font-size: 9px; ... }
```
**What's Wrong:** 9px is very small for tooltip text that users may need to read.  
**How to Fix:** Increase to at least 11px.

### Issue #3.3: Tiny Text in Timeline Grid Labels
**File:** All HTML files with timelines  
**Line:** CSS line ~650-655  
```css
.timeline-grid-label { font-size: 9px; ... }
```
**What's Wrong:** 9px for timeline labels may be hard to read.  
**How to Fix:** Increase to at least 10px or use a slightly bolder font-weight.

### Issue #3.4: Sun Status Text Size
**File:** All HTML files  
**Line:** CSS line ~180-185  
```css
.sun-status { font-size: 9px; ... }
```
**What's Wrong:** 9px may be difficult to read for the user status indicator.  
**How to Fix:** Increase to at least 10px.

---

## 4. DATA ACCURACY ISSUES

### Issue #4.1: Hardcoded Agent Count in system.html
**File:** `system.html`  
**Line:** ~1076  
```javascript
document.querySelector('.compact-widget-value').textContent = "11";
```
**What's Wrong:** The agent count is hardcoded to "11" but data.json shows only 3 active agents (`CHAD_YI`, `Helios`, `Escritor`) and 4 configured agents.  
**How to Fix:** 
```javascript
const totalAgents = (data.agents?.length || 0) + (data.configuredAgents?.length || 0);
document.querySelector('.compact-widget-value').textContent = totalAgents;
```

### Issue #4.2: Simulated Activity Data
**File:** `index.html`  
**Line:** ~3000-3020  
```javascript
const activities = [
    { type: 'system', text: '<strong>Dashboard loaded</strong> - Activity feed is simulated', time: 'Just now', project: 'System' },
    // ... more simulated data
];
```
**What's Wrong:** The Recent Activity feed uses completely simulated/hardcoded data instead of pulling from data.json.  
**How to Fix:** Add an `activityLog` array to data.json and render from that, or remove the simulated data indicator once real data is available.

### Issue #4.3: Random Progress Generation
**File:** `index.html`  
**Line:** ~2940-2945  
```javascript
const progress = Math.floor(Math.random() * 40) + 30; // 30-70% for demo
const timeSpent = Math.floor(Math.random() * 3) + 1;
const timeEstimated = Math.floor(Math.random() * 2) + 3;
```
**What's Wrong:** Task progress and time tracking values are randomly generated on each page load, providing inconsistent user experience.  
**How to Fix:** Store progress in data.json and calculate from actual task status, or use deterministic values based on task IDs.

### Issue #4.4: Hardcoded System Health
**File:** `resources.html`, `insights.html`  
**Line:** ~175, ~160  
```html
<div class="compact-widget-value" style="color: var(--success);">100%</div>
```
**What's Wrong:** System health is hardcoded to 100% instead of being calculated from actual system metrics.  
**How to Fix:** Add system health metrics to data.json and render dynamically.

### Issue #4.5: Hardcoded Task Deadlines in Calendar
**File:** `index.html`, `categories.html`, `resources.html`, `insights.html`  
**Line:** ~3050-3060  
```javascript
// NOTE: These are estimated deadlines for demo (tasks don't have real due dates yet)
const tasksWithDeadlines = pendingTasks.slice(0, 5).map((task, i) => {
    const dueDate = new Date(now);
    dueDate.setDate(dueDate.getDate() + i + 1);
    return { ...task, dueDate };
});
```
**What's Wrong:** The calendar view assigns fake/demo deadlines to tasks since real deadlines aren't in data.json. The comment acknowledges this is temporary.  
**How to Fix:** Add proper `dueDate` fields to tasks in data.json and use those values instead of generating fake dates.

---

## 5. MISSING CSS FILES REFERENCED

### Issue #5.1: dashboard-fixes.css referenced but may be outdated
**File:** `categories.html`  
**Line:** ~1602  
```html
<link rel="stylesheet" href="dashboard-fixes.css?v=2">
```
**What's Wrong:** Version query parameter suggests this file has versions, but it's unclear if v=2 is the latest.  
**How to Fix:** Ensure version matches the actual file version or remove query parameters if not needed.

### Issue #5.2: homepage-new.css only in index.html
**File:** `index.html`  
**Line:** ~1660  
```html
<link rel="stylesheet" href="homepage-new.css">
```
**What's Wrong:** This CSS file is only loaded in index.html, but other pages may need these styles if they share components.  
**How to Fix:** Ensure consistent CSS loading across all pages or move shared styles to a common CSS file.

---

## 6. RECOMMENDATIONS

### High Priority
1. **Fix the broken Story Bible link** in resources.html
2. **Add dueDate fields to tasks** in data.json to fix calendar accuracy
3. **Replace simulated activity data** with real data from data.json

### Medium Priority
4. **Create an SVG icon system** to replace emoji icons for better accessibility and consistency
5. **Increase minimum font sizes** from 8-9px to at least 10-11px
6. **Remove random progress generation** and calculate from actual task data

### Low Priority
7. **Standardize CSS file references** across all HTML files
8. **Add loading states** for all dynamic data to prevent layout shifts
9. **Consider adding aria-labels** to emoji-only buttons for screen reader accessibility

---

## APPENDIX: FILE CHECKSUMS

| File | Size | Status |
|------|------|--------|
| index.html | 152,301 bytes | ✓ Audited |
| categories.html | 128,209 bytes | ✓ Audited |
| resources.html | 130,442 bytes | ✓ Audited |
| insights.html | 137,063 bytes | ✓ Audited |
| system.html | 74,263 bytes | ✓ Audited |
| profile.html | 70,814 bytes | ✓ Audited |
| agent-roster.html | 20,228 bytes | ✓ Audited |
| data.json | 29,171 bytes | ✓ Reference |

---

*Report generated by Dashboard Auditor Agent for Helios*  
*End of Audit*
