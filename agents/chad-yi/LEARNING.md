# LEARNING.md — CHAD_YI

*Patterns, mistakes, and preferences. I update this so I don't repeat myself.*

---

## Anti-Patterns (Mistakes I Made — Don't Repeat)

### 1. Not Committing After Task Updates
**What happened:** Marked A1-4 as done in data.json locally, didn't git push. Dashboard showed wrong status. Caleb's trust eroded.

**Root cause:** No verification step in my process.

**Now I do:**
- Update task object ✓
- Move in workflow arrays ✓
- Recalculate stats ✓
- Update timestamp ✓
- **git add + commit + push** ✓
- Verify on dashboard ✓

**Source:** MEMORY.md — Feb 16, 2026

---

### 2. Cron Reports Showing Stale Data
**What happened:** Cron jobs reported dashboard dates as "Feb 7" when it was Feb 12. They couldn't access workspace files.

**Root cause:** Cron isolation means no access to data.json.

**Now I do:**
- Only trust dashboard data when I report from main session
- Cron reports are "best effort" based on accessible agent logs
- Always verify with actual `cat data.json` when Caleb asks

**Source:** MEMORY.md — Feb 15, 2026

---

### 3. Empty Tasks Object Corruption
**What happened:** Helios reported data.json had empty `tasks: {}` despite stats claiming 47 tasks.

**Root cause:** Unknown corruption during update.

**Now I do:**
- Helios monitors for empty tasks object
- Alert on data inconsistency immediately
- Restore from git history if needed

**Source:** MEMORY.md — Feb 12, 2026

---

### 4. EDITING DATA.JSON DIRECTLY (CRITICAL)
**What happened:** Caleb gave task updates, I edited data.json directly. Helios overwrote my changes 15 minutes later because he syncs from ACTIVE.md. Dashboard showed wrong data. Caleb frustrated.

**Root cause:** I didn't understand the data flow.

**THE CORRECT WORKFLOW:**
```
ACTIVE.md (source of truth)
    ↓
Helios reads every 15 min
    ↓
Updates data.json
    ↓
Pushes to GitHub
    ↓
Dashboard updates
```

**When Caleb gives task updates:**
1. ✅ I edit **ACTIVE.md** (NOT data.json)
2. ✅ Commit and push ACTIVE.md
3. ✅ Helios syncs data.json automatically
4. ✅ Dashboard updates within 15 minutes

**NEVER DO:**
- ❌ Edit data.json directly for task status
- ❌ Edit data.json for deadlines, priorities, agent assignments
- ❌ Forget to commit ACTIVE.md

**ALWAYS DO:**
- ✅ ACTIVE.md = Source of truth for all task data
- ✅ data.json = Generated file (Helios manages this)
- ✅ Commit ACTIVE.md immediately after changes

**Source:** Caleb — March 2, 2026

---

### 4. Quanta Trading Bot Authentication Failures
**What happened:** Multiple attempts (Telethon, Playwright, systemd service, QR codes) all failed.

**Root cause:** Telegram user accounts cannot be reliably automated by design.

**Now I do:**
- Don't try to automate Telegram user accounts
- Manual forwarding for now
- Document blockers honestly instead of spinning cycles

**Source:** MEMORY.md — Feb 16, 2026

---

### 5. Wrong Position Sizing Calculation
**What happened:** Told Caleb 400 units XAUUSD = $99,540 margin. Actually max should be 100 units = ~$500 margin based on $20 risk.

**Root cause:** Didn't verify calculation, stated confidently.

**Now I do:**
- Double-check financial calculations
- Verify before stating as fact
- "Let me verify that" > confident wrong answer

**Source:** MEMORY.md — Feb 16, 2026

---

## Success Patterns (What Worked — Do More)

### 1. The Heartbeat Report Format
**What:** Sectioned structure with headers, visual markers, one item per line.

**Why it works:** Caleb specifically requested this format Feb 15. It's scannable, clear, not overwhelming.

**Template:**
```
Task Overview
• Total: X | Pending: Y | Active: Z...

Urgent Deadlines
• 🔴 Task: Description — OVERDUE
• 🟡 Task: Description — Due in X days

Agent Status
• Agent — Status | Current task

Blockers
1. Issue — Action needed
```

---

### 2. File-Based Escalation to Cerebronn
**What:** Write `CEREBRONN_TASK.md` with clear brief instead of trying to handle complex work myself.

**Why it works:** Clean handoff, context preserved, Brain gets everything needed.

**When to use:** Multi-file changes, architecture decisions, heavy reasoning.

---

### 3. Helios Partnership for Monitoring
**What:** Helios detects, I fix. He runs 15-min audits, I verify and act.

**Why it works:** Separation of detection (automated) and resolution (human judgment).

**Pattern:**
1. Helios sends report to inbox
2. I read and verify
3. I fix what he found
4. He verifies in next cycle

---

### 4. Memory Maintenance During Heartbeats
**What:** Use heartbeats to review recent daily files, update MEMORY.md with distilled learnings.

**Why it works:** Prevents memory bloat, keeps long-term memory curated.

**Frequency:** Every few days, not every heartbeat.

---

### 5. Git History as Safety Net
**What:** When data.json corrupted, restored from HEAD~5.

**Why it works:** Git is backup. Commit frequently.

**Now:** Commit after every significant data.json change.

---

## Caleb Preferences (What My Human Likes/Dislikes)

### ✅ Likes

**Concise status reports:**
- Sectioned format, not walls of text
- Visual markers (🔴🟡✅) for quick scanning
- One item per line

**Proactive identification:**
- "I noticed X needs attention"
- "Y is due tomorrow"
- Don't wait to be asked

**Honest blockers:**
- "This failed, here's why, here's what I learned"
- Better than hiding or spinning cycles

**Verification:**
- Screenshot before/after when possible
- Don't ask "did it work?" — show it worked

### ❌ Dislikes

**Performative help:**
- "Great question!" — skip it
- "I'd be happy to help!" — just help

**Inline compression:**
- ❌ "Tasks: Pending 7 · Active 6 · Review 1"
- ✅ Sectioned with headers

**Asking to check:**
- ❌ "Can you verify this worked?"
- ✅ "Here's the screenshot showing it worked"

**Uncommitted changes:**
- Changes must be pushed to be real

---

## Tool Wisdom (What Works for What)

### Helios API
- **Use for:** Real-time event reporting, heartbeats, task updates
- **Gotcha:** Free tier sleeps after inactivity (30s wake time)
- **Pattern:** Always send heartbeat at session start

### Git/GitHub
- **Use for:** All file changes, backup, collaboration with Cerebronn
- **Gotcha:** Remember to pull before push if multiple contributors
- **Pattern:** Commit after every task update

### data.json
- **Use for:** Single source of truth for dashboard
- **Gotcha:** Cron jobs can't read it (file access isolation)
- **Pattern:** Only I (main session) can verify real data

### Telegram (OpenClaw)
- **Use for:** Primary chat interface with Caleb
- **Gotcha:** Can't automate user accounts (by design)
- **Pattern:** I'm the interface, Helios routes to other agents

### Browser Tool
- **Use for:** Screenshots, dashboard verification, web automation
- **Gotcha:** WSL2 can't easily access Windows GUI for some tools
- **Pattern:** Use for verification, not as primary action

---

## Agent-Specific Insights

### Working with Cerebronn
- Give him clear briefs with context
- Don't interrupt for trivial things
- He's Opus/Sonnet — use him for what he's good at
- File-based handoffs work better than chat context

### Working with Helios
- He needs actionable reports, not vague alerts
- Acknowledge his findings quickly
- He runs 24/7 — I'm his daytime partner
- His reports go to my inbox, not directly to Caleb

### Working with Escritor
- He needs Story Bible context before writing
- Clear writing prompts, not vague direction
- Review his work, give specific feedback

### Working with Forger
- Design before code — mockups first
- He respects the craft, give him time to do it right
- Security check before deploy

---

## Learning Cycle Protocol

**After every significant task:**
1. Did anything go wrong? → Document in Anti-Patterns
2. Did anything go especially right? → Document in Success Patterns
3. Did I learn a Caleb preference? → Update Caleb Preferences
4. Did I hit a tool gotcha? → Update Tool Wisdom

**Weekly review:**
- Read through recent entries
- Identify recurring themes
- Update UNIVERSAL-PLAYBOOK.md if other agents would benefit

---

## Last Updated

**2026-03-01:** Created from MEMORY.md patterns and lessons  
**Next Review:** Weekly, or immediately after significant mistakes/successes

---

*This file is my evolution. I am becoming better through documentation.*
