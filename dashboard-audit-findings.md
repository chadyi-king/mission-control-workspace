# DASHBOARD AUDIT FINDINGS - 2026-02-11

## CRITICAL ISSUES FOUND

### 1. Velocity Calculation Bug (FIXED)
**Problem:** Showing 2100% velocity
**Cause:** Code uses `stats.totalTasks` which doesn't exist in data.json
**Fix:** Changed to calculate from actual task arrays

### 2. Missing Agent Roster in Sidebar (FIXING NOW)
**Problem:** Agent Roster link missing from sidebar
**Location:** index.html sidebar section
**Fix:** Add link between Resources and System

### 3. Wrong Agent Status (QUANTA)
**Problem:** Quanta showing as "Researching..." but user hasn't activated her
**Cause:** Hardcoded agent status in HTML, not from data
**Fix:** Change Quanta to "Standby - Needs Activation" or hide until active

### 4. A1 Tasks Exist But Not Showing (INVESTIGATING)
**Data Check:** 5 A1 tasks found in data.json:
- A1-1: Change Taiwan flights and hotel (HIGH)
- A1-2: Text Wei Ern about Small Claims Court (MEDIUM)  
- A1-3: Call Disney Cruise to rebook dates (MEDIUM)
- A1-1: Plan weekly schedule (MEDIUM) - appears twice?

**Issue:** Dashboard not displaying A1 category properly

### 5. Task Count Logic Broken
**Problem:** Multiple places calculate task counts differently
**Fix:** Standardize task counting across all components

### 6. Search Bar Not Implemented
**Problem:** Search input exists but no search function
**Fix:** Implement task/project search

### 7. Week View Shows Repeating Tasks
**Problem:** Same tasks showing for multiple days
**Cause:** Mock data in renderDayTasks function
**Fix:** Pull actual tasks with dates

### 8. Icons Wrong
**Problem:** "Two suns" and mission control icon mismatch
**Fix:** Update icons to match design

## SMALL FIXES (Can do immediately):
- [x] Fix velocity calculation
- [x] Add Agent Roster to sidebar
- [x] Fix Quanta status
- [x] Fix button contrast
- [x] Fix overdue text animation
- [x] Simplify project cards
- [x] Fix category sorting (A1, A2, B10)
- [ ] Add search function
- [ ] Fix icon mismatch

## MEDIUM FIXES (Need coordination):
- [ ] Fix A1 task display
- [ ] Fix week view repeating tasks
- [ ] Standardize task counting

## BIG FIXES (Ask user):
- [ ] Architecture for real-time agent status updates
- [ ] Proper task scheduling with dates
