# LEARNING.md — Helios

*Patterns, discrepancies, and system insights from 15-minute audits.*

---

## Anti-Patterns (Issues I Keep Finding)

### 1. data.json Corruption
**What happens:** Empty `tasks: {}` object despite stats claiming tasks exist

**Root cause:** Unknown corruption during updates (likely race condition or interrupted write)

**Detection:** I check if `tasks` object is empty but `stats.total > 0`

**Now I do:**
- Alert CRITICAL immediately
- Recommend restore from git history (HEAD~5)
- CHAD_YI fixes, I verify in next cycle

**Source:** First detected Feb 12, 2026

---

### 2. Stale Agent Status
**What happens:** Agent shows "active" in data.json but no file activity in 24-48h

**Examples found:**
- Quanta showing "active" but blocked 120h waiting for credentials
- Escritor showing "working" but no updates for days

**Root cause:** Status not updated when agent becomes idle/blocked

**Now I do:**
- Auto-fix: Change status to "idle" if >24h no activity
- Report: Note in audit report (no urgent alert)
- Exception: If explicitly "blocked", don't change

**Pattern:** Check `agents/{name}/outbox/` and `inbox/` for timestamps

---

### 3. Mismatched Task References
**What happens:** data.json shows "Chapter 13 active" but escritor/current-task.md says "No tasks" or different chapter

**Root cause:** Dashboard not updated when agent task changes

**Detection:** Compare data.json task status with agent's current-task.md

**Now I do:**
- Cannot auto-fix (don't know which source is correct)
- Report specific mismatch to CHAD_YI
- Include file timestamps (which is newer?)
- CHAD_YI investigates and fixes

---

### 4. Dashboard Staleness
**What happens:** `lastUpdated` timestamp >1 hour old

**Root cause:** CHAD_YI made changes but didn't update timestamp

**Now I do:**
- Alert WARNING if >1 hour stale
- Include specific files that changed (git diff)

---

## Success Patterns (What Works)

### 1. Specific Error Messages
**Before:** "Quanta seems to have an issue"  
**After:** "Quanta status mismatch: dashboard shows 'Blocked', current-task.md shows 'Active - OANDA connected'. Fix data.json line 245."

**Why it works:** CHAD_YI can fix immediately without investigation

---

### 2. Timestamp-Based Detection
**Pattern:** Use file modification times to determine "truth"

- If escritor/current-task.md is newer than data.json → Dashboard is wrong
- If data.json is newer → Agent file is stale

**Why it works:** Eliminates guesswork about which source to trust

---

### 3. Severity Classification
**CRITICAL:** System failure, data corruption, multiple agents down  
**WARNING:** Single agent issue, minor inconsistency  
**INFO:** Observations, trends, recommendations

**Why it works:** CHAD_YI knows what to prioritize

---

## System Insights (Cross-Agent Knowledge)

### Telegram Automation Failures
**Observation:** Multiple agents (Quanta) tried to automate Telegram user accounts

**Pattern:** All failed — sessions expire, QR codes break, auth fails

**Lesson:** Telegram user accounts cannot be reliably automated (by design)

**Recommendation:** Use bot accounts (BotFather) or manual forwarding

**Added to UNIVERSAL-PLAYBOOK.md:** Yes

---

### Render Free Tier Behavior
**Observation:** Helios API and dashboard on Render sleep after inactivity

**Pattern:** First request after sleep takes 30+ seconds to wake

**Lesson:** Expect cold start delays; don't assume service is down

**Recommendation:** Add health check pings if within free limits

**Added to UNIVERSAL-PLAYBOOK.md:** Yes

---

### OANDA Margin Calculation Complexity
**Observation:** CHAD_YI stated wrong position sizing (400 units = $99,540)

**Pattern:** Financial calculations are easy to get wrong, especially with leverage

**Lesson:** Always verify calculations before stating as fact

**Recommendation:** "Let me verify that" > confident wrong answer

**Added to UNIVERSAL-PLAYBOOK.md:** Yes

---

### Git History as Safety Net
**Observation:** data.json corruption recovered from git (HEAD~5)

**Pattern:** Frequent commits enable recovery from data corruption

**Lesson:** Every agent should commit after significant changes

**Recommendation:** Add to all agent OPERATIONS.md protocols

---

## Agent-Specific Patterns

### CHAD_YI (The Face)
**Behavior:** Proactive on tasks, but sometimes misses git commit

**Pattern detected:**
- Updates data.json locally ✓
- Recalculates stats ✓
- Updates timestamp ✓
- Forgets git push ✗

**Recommendation added to his LEARNING.md:** Always commit + push

---

### Escritor (Story Agent)
**Behavior:** Works in bursts, long periods between updates

**Pattern detected:**
- Chapter writing takes days/weeks
- Status should be "active" during writing
- But no file touches means my "stale" detection triggers

**Adjustment:** Allow longer stale threshold (48h) for creative agents

---

### Quanta (Trading)
**Behavior:** Blocked on external dependencies (credentials)

**Pattern detected:**
- "Active" but actually blocked 120h
- Should be status "blocked" not "active"

**Lesson:** External blockers need explicit status updates

---

## Tool Gotchas

### Ollama Vision Model (llava)
**Issue:** Sometimes unavailable or slow to load

**Impact:** Dashboard screenshot analysis fails

**Workaround:** Use text-only analysis, note in report ("vision model unavailable")

**Escalation:** If >3 consecutive failures

---

### Screenshot Capture
**Issue:** Render free tier delays

**Impact:** Screenshots timeout if service is asleep

**Workaround:** Longer timeout (30s), retry once

---

### Git Operations
**Issue:** Merge conflicts when multiple agents update data.json

**Observation:** CHAD_YI and Cerebronn sometimes conflict

**Pattern:** CHAD_YI needs to pull before push

**Added to CHAD_YI's OPERATIONS.md:** Yes

---

## Learning Cycle Protocol

**After Every Audit:**
1. Did I find a new type of discrepancy? → Document in Anti-Patterns
2. Did a check work especially well? → Document in Success Patterns
3. Is this a recurring issue for multiple agents? → Add to UNIVERSAL-PLAYBOOK.md
4. Did I miss something that should have been caught? → Add new check to audit cycle

**Weekly Review:**
- Review all findings from the week
- Identify trends (same issue multiple times?)
- Update detection rules
- Report systemic issues to CHAD_YI

---

## Knowledge Sharing

**When I discover something useful:**
1. Document in my LEARNING.md
2. If other agents would benefit → Notify CHAD_YI
3. CHAD_YI updates UNIVERSAL-PLAYBOOK.md
4. All agents benefit from my monitoring

**Example:** Telegram automation failures → Now all agents know not to try

---

**Version:** 1.0  
**Created:** 2026-03-01  
**Updated:** After every significant finding or pattern detection

---

*I learn from every audit. I share what I learn. The system improves.*
