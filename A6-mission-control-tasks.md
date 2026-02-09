# A6 - Mission Control Dashboard (Project)

**Category:** A - Ambition by Calbee (Personal)  
**Project Code:** A6  
**Status:** Active development  
**Owner:** Caleb E via Chad Yi agent  
**Last Updated:** 2026-02-05

---

## PROJECT OVERVIEW
Build a fully functional Mission Control Dashboard hosted on GitHub Pages for tracking all A/B/C category projects, agent execution, and task management.

---

## TASKS

### Task 1: Design Visual System (YOU decide priority)
**Status:** In Progress  
**Description:** Create luxury high-tech visual design (not just flat black)

**Subtasks (I can run agents on these):**
- [ ] **1.1 Research luxury dashboard references**
  - Search Behance/Dribbble for "luxury dark dashboard"
  - Find high-tech/gaming UI inspirations
  - Collect color palettes beyond black
  
- [ ] **1.2 Implement glassmorphism effects**
  - Frosted glass panels with blur
  - Translucent overlays
  - Light refraction effects
  
- [ ] **1.3 Add dynamic background**
  - Subtle gradient mesh (not flat black)
  - Animated particles or floating elements
  - Grid lines or circuit patterns
  
- [ ] **1.4 Create premium card designs**
  - 3D tilt effects on hover
  - Inner shadows and depth layers
  - Gradient borders with glow

---

### Task 2: Build Core Navigation (YOU decide priority)
**Status:** In Progress  
**Description:** Sidebar with 6 sections, collapsible, all 18 projects

**Subtasks:**
- [ ] **2.1 Create collapsible sidebar component**
  - Collapse/expand button with animation
  - Icon-only mode when collapsed
  - Smooth transitions
  
- [ ] **2.2 Build category accordion system**
  - A/B/C expandable sections
  - Project links under each category
  - Active state highlighting
  
- [ ] **2.3 Add all 18 projects to navigation**
  - A1-A6 (6 projects)
  - B1-B10 (10 projects)
  - C1-C2 (2 projects)

---

### Task 3: Build Home Dashboard (YOU decide priority)
**Status:** In Progress  
**Description:** Task-focused homepage with real-time agent status

**Subtasks:**
- [ ] **3.1 Create live agent cards**
  - Progress bars with animation
  - Status indicators (pulsing dots)
  - Agent names and assigned tasks
  
- [ ] **3.2 Build stats widgets**
  - Token cost tracking display
  - Time spent today counter
  - Completion rate visualization
  
- [ ] **3.3 Add quick action buttons**
  - Spawn Agent (primary)
  - Smack All Agents
  - Pause/Resume controls
  
- [ ] **3.4 Create activity feed**
  - Recent agent completions
  - Error notifications
  - Task additions

---

### Task 4: Implement Data System (YOU decide priority)
**Status:** Pending  
**Description:** GitHub JSON polling for 30s refresh

**Subtasks:**
- [ ] **4.1 Create data.json structure**
  - Schema for agents, tasks, stats
  - Sample data for testing
  
- [ ] **4.2 Add polling to dashboard**
  - Fetch data.json every 30 seconds
  - Update UI without page reload
  - Handle errors gracefully
  
- [ ] **4.3 Connect to GitHub API**
  - Authenticate gh CLI
  - Push data.json updates
  - Test update propagation

---

### Task 5: Mobile Responsive Design
**Status:** Backlog  
**Description:** Make dashboard work on phones

**Subtasks:**
- [ ] **5.1 Research mobile dashboard patterns**
  - Bottom navigation vs hamburger
  - Card layouts for small screens
  
- [ ] **5.2 Implement responsive breakpoints**
  - Tablet layout (768px)
  - Mobile layout (375px)
  - Touch-friendly buttons
  
- [ ] **5.3 Test on actual devices**
  - iPhone Safari
  - Android Chrome

---

### Task 6: Build Project Detail Pages
**Status:** Backlog  
**Description:** Individual pages for all 18 projects with tasks/subtasks

**Subtasks:**
- [ ] **6.1 Create A category project pages**
  - A1: Personal Tasks (+ Wedding subtasks)
  - A2: RE:UNITE (chapters, uploads)
  - A3: KOE
  - A4: Streaming
  - A5: Trading
  - A6: Mission Control (this file)
  
- [ ] **6.2 Create B category project pages**
  - B1-B10: All business empire projects
  
- [ ] **6.3 Create C category project pages**
  - C1: Real Estate
  - C2: Side Sales
  
- [ ] **6.4 Add task/subtask expand system**
  - Click project → show tasks
  - Click task → show subtasks
  - "Spawn Agent" buttons on each

---

### Task 7: Integrate OpenClaw Backend
**Status:** Backlog  
**Description:** Real agent spawning and status updates

**Subtasks:**
- [ ] **7.1 Connect sessions_spawn API**
  - Button triggers actual agent spawn
  - Pass task context to agent
  
- [ ] **7.2 Implement agent status tracking**
  - Read from OpenClaw session list
  - Update progress in real-time
  
- [ ] **7.3 Auto-update data.json**
  - Hook into agent lifecycle
  - Write updates automatically

---

## DECISIONS LOG

**2026-02-05**
- ❌ Current design: "Just black, not luxurious or high-tech"
- ✅ Need: Glassmorphism, dynamic backgrounds, premium effects
- ❌ Not mobile responsive (Task 5 added)
- ✅ Hierarchy confirmed: Categories → Projects → Tasks → Subtasks
- ✅ I decide subtasks, you decide tasks
- ✅ I can spawn agents on subtasks

---

## NEXT ACTIONS

**Your decision needed:** Which Task (1-7) should I focus on first?

**Recommendation:** 
1. **Task 1** (Visual upgrade) - make it actually look luxury/high-tech
2. **Task 2** (Navigation) - fix sidebar collapse and project listing
3. Then others based on priority
