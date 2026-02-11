# 🤖 AUTOMATED AGENT WORKFLOW - ACTIVE

## Schedule Overview (Singapore Time)

### 🌅 8:00 AM - MORNING BRIEFING (Daily)
**To You:** Full report
- Tasks needing your attention today
- What each agent is working on  
- Urgent deadlines
- Dashboard health status

### ☀️ 10 AM - 10 PM - EVERY 2 HOURS
**To You:** Brief check-in
- Summary of what's happening
- Any issues that need your input
- Progress on active tasks

### 🌙 12 AM - 6 AM - EVERY 3 HOURS
**Silent mode** - Only alert if CRITICAL

### 🔄 EVERY HOUR (Internal)
**Me + Helios coordination (no message to you)**
- Check agent message bus
- Helios audits dashboard
- Fix small issues automatically
- Queue bigger issues for your next report

---

## 🎯 DECISION FRAMEWORK

### I EXECUTE AUTOMATICALLY:
- CSS fixes, typos, layout adjustments
- Data.json updates (when you give me tasks)
- Deploying changes to GitHub
- Small bug fixes
- Dashboard health checks

### I ASK YOU FIRST:
- Architecture changes (backend API, new systems)
- Design decisions (colors, layout, major UI changes)
- Cost-related decisions (API keys, paid services)
- Agent spawning (when to activate Quanta, etc.)
- Conflicting priorities

### HELIOS DOES:
- Audits dashboard every check
- Reports issues to me
- I fix → Confirm with Helios → Report to you

---

## 📝 HOW TO GIVE ME TASKS

**Just message me naturally:**
- "Add task: Review Chapter 13 by Friday" 
- "Helios needs to fix the sorting bug"
- "Quanta should start researching trading APIs"

**I'll:**
1. Parse the task
2. Update data.json
3. Deploy to GitHub
4. Confirm with agent (Helios verifies)
5. Report back to you

---

## 🚨 ESCALATION RULES

**I message you immediately if:**
- Dashboard is down/broken
- Agent reports critical blocker
- You have urgent deadline in < 24h
- I can't fix something automatically

**I batch for next scheduled report:**
- Minor fixes completed
- Progress updates
- Non-urgent questions
- General status

---

## ✅ CURRENT STATUS

**Active Cron Jobs:**
1. ✅ Morning Briefing (8 AM daily)
2. ✅ Day Check-ins (every 2 hours, 10 AM - 10 PM)
3. ✅ Night Checks (every 3 hours, silent)
4. ✅ Internal Coordination (every hour)

**Agents:**
- **CHAD_YI (Me):** Brain, coordinator, executor
- **Helios:** Auditor, checker, reporter
- **Escritor:** On standby (activate when needed)
- **Quanta:** On standby (activate when needed)

**Next Morning Briefing:** Tomorrow 8 AM SGT
