# PHASE 2 BUILD PLAN
## Helios COO + Dashboard Integration

**Start Time:** 2026-02-13 00:43 SGT  
**ETA:** 4 hours  
**Status:** STARTING

---

## TASK BREAKDOWN

### Task 1: Install Ollama Models (15 min)
**Status:** 🔴 BLOCKED - Needs Caleb
**Steps:**
1. Pull qwen2.5:7b (~5GB)
2. Pull llava:13b (~8GB)
3. Verify models load

**Deliverable:** Both models available in Ollama

**Your Action Required:**
```bash
ollama pull qwen2.5:7b
ollama pull llava:13b
```

---

### Task 2: Create Helios Audit Script (45 min)
**Status:** ✅ COMPLETE
**Completed:** 00:47
**Deliverable:** agents/helios/helios-audit.py
**Test Result:** Works, 72 tasks verified, 2 warnings (expected)

---

### Task 3: Install Helios Service (30 min)
**Status:** 🔴 BLOCKED - Needs sudo
**Steps:**
1. Copy helios.service to /etc/systemd/system/
2. Run systemctl daemon-reload
3. Enable service
4. Start service
5. Verify running

**Your Action Required:**
```bash
cd /home/chad-yi/.openclaw/workspace
sudo cp agents/helios/helios.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable helios
sudo systemctl start helios
sudo systemctl status helios
```

**Deliverable:** systemctl status shows "active (running)"

---

### Task 4: Test Audit Cycle (30 min)
**Status:** ⏸️ PENDING
**Steps:**
1. Wait for first audit (15 min)
2. Check agents/helios/outbox/ for report
3. Verify all agents audited
4. Check data integrity verified

**Deliverable:** Audit report generated

---

### Task 5: Dashboard System Health Section (1 hour)
**Status:** ⏸️ PENDING
**Steps:**
1. Update mission-control-dashboard/index.html
2. Add System Health section
3. Add agent compliance display
4. Add overall health indicator
5. Style with CSS

**Deliverable:** Dashboard shows health status

---

### Task 6: Dashboard Activity Feed (45 min)
**Status:** ⏸️ PENDING
**Steps:**
1. Read DATA/data.json activity field
2. Display recent events
3. Style as feed/list
4. Auto-refresh with page

**Deliverable:** Activity feed visible

---

### Task 7: Integration Testing (45 min)
**Status:** ⏸️ PENDING
**Steps:**
1. Verify Helios updates DATA/data.json
2. Verify dashboard displays updates
3. Test blocked item workflow
4. Full end-to-end test

**Deliverable:** System working end-to-end

---

## CURRENT STATUS

**Completed:** 0 of 7 tasks (0%)  
**Blocked:** Task 1 (waiting for Ollama models)  
**Next Action:** You run ollama pull commands

---

## PROGRESS LOG

### 00:43 - START
- Plan created
- Ready to execute
- Waiting on Ollama models

