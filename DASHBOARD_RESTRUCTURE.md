# Mission Control Dashboard Restructure Plan

## Current Problems
- Too many stats on home page (6 stat cards)
- Not task-focused enough
- Workflow pipeline shows pending but not actionable

## Proposed Restructure

### New Home Layout: Task-Centric

#### Top Section: Priority Tasks (NEW)
```
┌─────────────────────────────────────────────────────────┐
│ 🔴 URGENT (Due < 3 days)        🟡 HIGH (Due < 7 days) │
│ ───────────────────────────────────────────────────────│
│ • B6-1: 120 facilitators        • A3-1: KOE Script 1   │
│   Due: Feb 17                    Due: Feb 15           │
│ • B6-3: SPH items               • A1-1: Taiwan flights │
│   Due: Feb 17                    Due: Feb 13           │
└─────────────────────────────────────────────────────────┘
```

#### Middle Section: Active Work
```
┌─────────────────────────────────────────────────────────┐
│ 📋 ACTIVE TASKS              🔄 IN PROGRESS             │
│ ───────────────────────────────────────────────────────│
│ • A6-14: Project Tasks List  • A6-13: Project Detail   │
│   Assigned: Helios            Assigned: You             │
│                                                            │
│ • A2-4: Write Chapter 13     • (Empty state)           │
│   Assigned: Escritor                                    │
└─────────────────────────────────────────────────────────┘
```

#### Bottom Section: Quick Stats (MINIMAL)
```
┌─────────────────────────────────────────────────────────┐
│ Tasks: 67 total │ Done: 21 │ Pending: 49 │ Focus: B6   │
└─────────────────────────────────────────────────────────┘
```

### Remove from Home
- ❌ 6 individual stat cards (consolidate to 1 line)
- ❌ Separate workflow/decisions/calendar panels
- ❌ Queue panel (integrate into tasks)

### Keep/Enhance
- ✅ Quick Actions dropdown
- ✅ Project categories sidebar
- ✅ Red Sun avatar (your branding)

### Design Fixes Needed
1. **Task Cards:** Smaller, denser, due dates prominent
2. **Color Coding:** 
   - Red = Overdue/Urgent
   - Yellow = Due soon
   - Green = On track
3. **Mobile:** Better task list view
4. **Empty States:** Clear "Nothing urgent" messages

## Implementation Order
1. Real-time data service
2. Dashboard layout restructure (this file)
3. Design polish

## User Requirements
- See URGENT tasks immediately
- See HIGH priority tasks
- Track active/in-progress work
- Minimal stats (just counts)
- Clean, actionable interface
