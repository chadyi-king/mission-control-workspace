# A6 - Mission Control Dashboard (Chad Yi Infrastructure)

**Category:** A - Ambition by Calbee (Personal)  
**Project Code:** A6  
**Status:** Active development  
**Owner:** Caleb E via Chad Yi agent  
**Last Updated:** 2026-02-05

---

## 🎯 CURRENT SPRINT

### In Progress
- [ ] Build dashboard with GitHub JSON polling (30s refresh)
- [ ] Wait for user to auth `gh` CLI at home
- [ ] Deploy updated dashboard to GitHub Pages

### Blocked
- [ ] Push changes to GitHub repo (waiting for `gh auth login`)
- [ ] Implement real-time agent spawning (need API connection)

### Backlog
- [ ] Build all 17 project detail pages (A1-A5, B1-B10, C1-C2)
- [ ] Add task/subtask expand functionality
- [ ] Connect to OpenClaw backend for live agent status
- [ ] Add Google Drive integration (Resources section)
- [ ] Mobile responsive design
- [ ] Add neumorphism visual effects

---

## 📋 DECISIONS LOG

**2026-02-05**
- ✅ Removed "Execute" section (execution happens via me, dashboard reflects)
- ✅ 6 sections final: Home, Categories, Insights, Resources, System, Profile
- ✅ Home = task-centric (not project-centric)
- ✅ Dark theme + crimson accents confirmed
- ✅ GitHub JSON polling approach accepted (30s delay, I am the hub for now)
- ✅ User will auth `gh` CLI later to enable me pushing updates

---

## 🔧 TECHNICAL NOTES

**File Locations:**
- Complete dashboard: `./mission-control-complete.html`
- Need to rename to `index.html` and push to GitHub

**GitHub:**
- Repo: `chadyi-king/mission-control-dashboard`
- URL: https://chadyi-king.github.io/mission-control-dashboard/

**Pending Setup:**
- GitHub CLI installed at: `/home/chad-yi/.local/bin/gh`
- User needs to run: `export PATH="$HOME/.local/bin:$PATH" && gh auth login`

---

## 🚀 NEXT ACTIONS

1. **Immediate:** Update dashboard code to poll `data.json`
2. **When user ready:** Guide through `gh auth login`
3. **After auth:** Push updated dashboard + create `data.json`
4. **Then:** Build project detail pages starting with A2 (RE:UNITE)

---

## 💡 IDEAS FOR LATER

- Auto-generate daily summary from actual OpenClaw session data
- Agent self-reporting to database (reduce dependency on me)
- Integration with Telegram bot for mobile updates
- Wedding countdown widget with actual task list
- Token cost tracking from OpenClaw usage data
