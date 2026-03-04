# Mission Control Dashboard - Infrastructure Upgrade Plan
## Keeping YOUR Design, Adding Backend Features

### YOUR DESIGN (Untouched)
- ✅ Dark theme (OLED black #0a0a0a)
- ✅ Green accent (#1a5f4a) + Gold (#f4a261)
- ✅ Stats grid layout (5 cards)
- ✅ Task list (table view)
- ✅ Project category cards (A/B/C)
- ✅ Typography (Inter + Playfair Display)

### CHANGES (Backend Only)

#### 1. Database (Day 1) - INVISIBLE TO YOU
**Current:** Read data.json  
**New:** Read SQLite database  
**Visual:** NO CHANGE

**Code change in dashboard:**
```javascript
// OLD
fetch('data.json')

// NEW  
fetch('/api/tasks')  // Reads from SQLite
```

**Your view:** Exact same dashboard, faster loading

---

#### 2. Real-time Updates (Day 2) - SMALL INDICATOR
**Current:** Refresh page to see updates  
**New:** Auto-refresh every 30 seconds + live indicator  
**Visual:** Small "Live" dot in header (green when connected)

**Code change:**
```javascript
// Add to header
<span class="live-indicator">● Live</span>

// Auto-refresh data every 30s
setInterval(loadData, 30000);
```

**Your view:** Same design, data updates automatically

---

#### 3. Cost Tracking (Day 3) - NEW OPTIONAL PANEL
**Current:** No cost data  
**New:** Optional cost panel (hidden by default)  
**Visual:** Toggle button "Show Costs" → reveals panel below stats

**Code change:**
```javascript
// Add toggle button (small, unobtrusive)
<button onclick="toggleCosts()">💰 Costs</button>

// Panel appears below stats when clicked
<div id="costPanel" style="display:none">
  Daily: $12.50 | Monthly: $340.00
</div>
```

**Your view:** Same design, optional cost view

---

#### 4. Agent Controls (Day 4) - ADMIN PANEL
**Current:** View agent status only  
**New:** Start/Stop buttons + log viewer  
**Visual:** "Agent Admin" link in footer → opens modal/popup

**Code change:**
```javascript
// Footer link
<a href="#" onclick="showAgentAdmin()">Agent Admin</a>

// Modal popup (doesn't change main view)
<modal id="agentAdmin">
  [Start] [Stop] [Restart] buttons
  Log viewer
</modal>
```

**Your view:** Same design, admin tools in modal

---

## ✅ WHAT STAYS EXACTLY THE SAME

| Element | Status |
|---------|--------|
| Dark background | ✅ Unchanged |
| Stats grid layout | ✅ Unchanged |
| Task table format | ✅ Unchanged |
| Project cards | ✅ Unchanged |
| Color scheme | ✅ Unchanged |
| Fonts | ✅ Unchanged |
| Responsive breakpoints | ✅ Unchanged |
| Animations/transitions | ✅ Unchanged |

---

## 🛠️ IMPLEMENTATION

**Step 1:** Create SQLite database (invisible)  
**Step 2:** Add API endpoint /api/tasks (backend)  
**Step 3:** Dashboard reads from API instead of JSON  
**Step 4:** Add live indicator dot (small, header)  
**Step 5:** Add cost toggle (optional, hidden by default)  
**Step 6:** Add agent admin modal (footer link)

---

## ⏱️ TIMELINE

- **Day 1:** Database + API (no visual change)
- **Day 2:** Live indicator + auto-refresh (small dot in header)
- **Day 3:** Cost panel (toggle button, hidden by default)
- **Day 4:** Agent admin modal (footer link)

**Total visual changes:**
- 1 green dot (live indicator)
- 1 toggle button (costs)
- 1 footer link (admin)

**Everything else stays exactly as you designed it.**

---

## ❓ PROCEED?

Start with database (invisible change)?
