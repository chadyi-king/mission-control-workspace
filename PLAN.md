# CHAD_YI Operational Plan - Memory, Agents, Workflow

## 1. MEMORY MANAGEMENT PLAN

### Current Problems:
- Hallucinating data (e.g., "Japan trip" vs "Taiwan flights")
- Overconfidence in stored data
- Not verifying against actual conversations

### Solution - Triple Verification:

**Before ANY data-based statement:**
1. **Check data.json** (stored data)
2. **Check memory files** (user conversations)
3. **Verify with user** if discrepancy found

**Memory Hierarchy:**
```
Priority 1: What user JUST said (working memory)
Priority 2: MEMORY.md (curated facts)
Priority 3: memory/YYYY-MM-DD.md (daily logs)
Priority 4: data.json (structured data) ← Verify before using
```

**Golden Rule:**
> "If I haven't seen it confirmed in the last 24h, I ask before stating it as fact."

### Memory Update Protocol:

**After EVERY significant conversation:**
1. Update `memory/YYYY-MM-DD.md` (daily log)
2. If decision made → Update `MEMORY.md` (long-term)
3. If task changed → Update `data.json` (only after user confirms)

**Before stating facts:**
```
User asks: "What's my A1-1 task?"
I do:
1. Check data.json → "Japan trip"
2. Check MEMORY.md → "Taiwan flights"
3. Check today's memory → User said "Taiwan" 2 hours ago
4. I say: "You mentioned Taiwan flights to rebook to April 15-19. Is that correct?"
5. After confirmation → Update data.json
```

---

## 2. AGENT ORCHESTRATION PLAN

### Current Problems:
- Agents not spawned
- No clear communication protocol
- Blocked agents waiting for input

### Solution - Clear Protocol:

**Agent Lifecycle:**
```
1. CONFIGURED (files exist) → CHAD_YI spawns → 2. IDLE (ready)
                                            ↓
3. ACTIVE (working) ← Helios assigns task ← Helios detects need
       ↓
4. REVIEW (done) → CHAD_YI approves → 5. DONE
```

**Communication Flow:**
```
User Request → CHAD_YI (me)
     ↓
Spawn Agent? → Create agent inbox
     ↓
Helios detects → Assigns task
     ↓
Agent works → Reports to outbox
     ↓
Helios reviews → Updates dashboard
     ↓
CHAD_YI reviews → User approval
     ↓
Mark complete
```

**Weekly Agent Check (Every Monday):**
- Review all agent statuses
- Spawn idle agents if tasks ready
- Clear blockers if inputs received
- Archive completed tasks

### Agent Responsibilities Matrix:

| Agent | Model | Status | Next Action | Blocker |
|-------|-------|--------|-------------|---------|
| CHAD_YI | kimi-k2-thinking | Active | Awaiting TeamViewer setup | None |
| Helios | kimi-k2-thinking | Active | 15-min audits | None |
| Escritor | qwen2.5:7b (Ollama) | Not spawned | A2-12 outline | Needs spawn command |
| Quanta | codellama:7b (Ollama) | Not spawned | Trading bot | Needs OANDA creds |
| MensaMusa | TBD (Ollama) | Not spawned | Options monitoring | Needs Moomoo creds |
| Autour | TBD (Ollama) | Not spawned | KOE scripts | Needs spawn command |

---

## 3. WORKFLOW IMPROVEMENTS

### Before Starting Any Task:

**Step 1: Clarify with User**
- Confirm task details
- Confirm deadline
- Confirm priority
- Confirm my understanding

**Step 2: Check Dependencies**
- What do I need? (files, access, credentials)
- What is blocked?
- Can I do this now or wait?

**Step 3: Estimate & Commit**
- How long will this take?
- When will I report back?
- What's the success criteria?

**Step 4: Execute & Verify**
- Do the work
- Test it works
- Screenshot/proof before saying "done"

**Step 5: Report & Document**
- Tell user what was done
- Update memory
- Update dashboard

### Anti-Hallucination Checklist:

Before saying something is "done":
- [ ] I actually did the work
- [ ] I verified it works
- [ ] I have proof (screenshot, file, output)
- [ ] I updated memory
- [ ] I didn't make up details

### Daily Routine (CHAD_YI):

**Morning (8 AM):**
- Check HEARTBEAT.md
- Review urgent deadlines
- Check agent statuses
- Plan day's work

**During Day:**
- Work on user requests
- Update progress
- Ask when unclear

**Evening (10 PM):**
- Update memory/YYYY-MM-DD.md
- Check what wasn't done
- Plan tomorrow

---

## 4. DESKTOP AGENT IMPROVEMENTS

### Current Issues:
- Screenshots not displaying in browser
- No OCR to read text from images
- No automatic action mode
- Must restart ngrok each time

### Improvements to Build:

#### A. Fix Screenshot Display

**Problem:** Image not showing in web UI
**Solution:** Fix the base64 encoding or use direct file serving

```python
@app.route('/screenshot/latest')
def latest_screenshot():
    # Get most recent screenshot file
    files = sorted(SCREENSHOT_DIR.glob('*.png'))
    if files:
        return send_file(files[-1], mimetype='image/png')
    return "No screenshots yet"
```

#### B. Add OCR (Text Recognition)

**Purpose:** Read text from screenshots automatically

```python
import pytesseract
from PIL import Image

def read_text_from_screenshot(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text

# Use case: Read Telegram signal text from screenshot
```

#### C. Automatic Action Mode

**Current:** Manual click/type only
**Improvement:** Auto-detect and act

```python
# Detect if Telegram has new message
def check_telegram_notification():
    screenshot = pyautogui.screenshot()
    # Look for notification badge
    # If found, click Telegram, read message, trade
```

#### D. Persistent ngrok URL

**Current:** New URL each restart
**Improvement:** Static subdomain (requires paid ngrok or alternative)

**Alternative:** Use `localtunnel` or `serveo` for free static-ish URLs

#### E. Safety Improvements

**Add confirmation for risky actions:**
- Before clicking "Buy" on trading platform → Screenshot, ask user
- Before typing passwords → Stop, ask permission
- Before closing windows → Confirm

#### F. Better Logging

**Current:** Simple text log
**Improvement:** Structured JSON logs

```json
{
  "timestamp": "2026-02-11T22:30:00Z",
  "action": "click",
  "coordinates": [500, 300],
  "context": "Clicked Buy button on OANDA",
  "screenshot": "screenshot_20260211_223000.png"
}
```

#### G. Macro Recording

**Feature:** Record and replay sequences

```python
# User records: "Open Chrome, go to OANDA, login"
# Agent saves sequence
# Later: "Execute OANDA login macro"
```

### Implementation Priority:

1. **Fix screenshot display** (Critical - user can't see results)
2. **Add OCR** (Critical - for reading signals)
3. **Safety confirmations** (Critical - prevent accidents)
4. **Persistent tunnel** (Nice to have)
5. **Macro recording** (Future enhancement)

---

## APPROVAL CHECKPOINT

**Before implementing anything above, user must approve:**

1. Memory plan acceptable?
2. Agent orchestration plan acceptable?
3. Workflow improvements acceptable?
4. Desktop agent improvements priority correct?

**What should I build first?**
