# Escritor Agent Implementation Plan

## Current Status
- **Agent:** Escritor (A2 - Story Agent)
- **State:** Configured but NOT spawned as persistent session
- **Current Task:** A2-13 Study Phase (90 questions)
- **Next:** Write RE:UNITE Chapter 13 after study approval

---

## Escritor's Purpose

**Project A2:** RE:UNITE - R21 Isekai Novel
- Weekly chapter releases on Google Drive site
- Story already has 12 chapters written
- Escritor needs to demonstrate deep understanding before continuing

**Role:** Master storyteller, continuity guardian, creative writer

---

## Implementation Plan

### Phase 1: Study Phase (Current - A2-13)

**What Escritor Does:**
1. **Read Source Materials:**
   - Story Bible (world rules, magic system, characters)
   - Chapters 1-12 (continuity, voice, style)
   
2. **Answer 90 Study Questions:**
   - Characters (25 questions) - Ryfel's SEAL mindset, Kriscila's promise
   - Magic System (20 questions) - Ether vs mana mechanics
   - World/Setting (20 questions) - Runevia prison system
   - Continuity (15 questions) - Capture event, callbacks
   - Style (10 questions) - Tone, formatting, structure

3. **Output:**
   - Save answers to `/agents/escritor/outbox/study-answers.md`
   - Wait for Caleb's review and corrections
   - Only proceed after approval

**Success Criteria:**
- All 90 questions answered
- Specific chapter references
- Honest about uncertainties

---

### Phase 2: Chapter Writing (After Study Approval)

**Workflow for Each Chapter:**

1. **Pre-Writing:**
   - Review previous chapter ending
   - Check continuity notes
   - Understand chapter objective

2. **Drafting:**
   - Write 3,000-5,000 words
   - Maintain character voices
   - Advance plot + character arcs

3. **Self-Review:**
   - Check against Story Bible
   - Verify continuity
   - Polish prose

4. **Submit to Caleb:**
   - Save to `/agents/escritor/outbox/chapter-XX-draft.md`
   - Report to Helios/CHAD_YI
   - Wait for feedback

5. **Revision:**
   - Address Caleb's notes
   - Final polish
   - Mark complete

---

## Agent Architecture

### File Structure
```
/agents/escritor/
├── SOUL.md                 # Who Escritor is (✅ exists)
├── SKILL.md                # How to write (✅ exists)
├── MEMORY.md               # Story continuity (✅ exists)
├── current-task.md         # What he's doing now (✅ exists)
├── AGENT_STATE.json        # Persistent state (✅ exists)
├── heartbeat.json          # Last activity (✅ exists)
├── inbox/                  # Messages to Escritor
│   └── study-questions.md  # 90 questions (✅ exists)
├── outbox/                 # Escritor's outputs
│   ├── study-answers.md    # His answers (to be created)
│   └── chapter-13-draft.md # Future chapters
└── projects/
    └── A2-reunite/         # Working files
```

### Communication Protocol

**Helios → Escritor (every 15 min):**
- Check if study questions complete
- Ask for progress update
- Request ETA

**Escritor → Helios:**
- Report progress (% complete)
- Flag blockers (questions unclear)
- Submit completed work

**Escritor → CHAD_YI:**
- Daily progress summary
- Questions needing clarification
- Completed drafts for review

---

## Running Escritor

### Option A: File-Based (Current)
- Escritor runs on-demand when CHAD_YI prompts
- Reads files, writes answers
- No persistent session
- **Good for:** Study phase (one-time task)

### Option B: Persistent Session (Recommended)
- Spawn Escritor as continuous agent
- He works autonomously on chapters
- Self-motivated, reports progress
- **Good for:** Ongoing chapter production

### Recommended: Hybrid Approach

**Phase 1 (Study):** File-based
- Run Escritor once to complete 90 questions
- Review and approve answers
- Takes 1-2 days

**Phase 2 (Writing):** Persistent session
- Spawn Escritor as ongoing agent
- He writes chapters weekly
- Reports to Helios/CHAD_YI
- Continuous operation

---

## Monitoring & Reporting

### Helios Checks:
1. **Study Phase:**
   - How many questions answered?
   - Any blockers?
   - ETA for completion?

2. **Writing Phase:**
   - Current chapter progress
   - Word count
   - Time since last update
   - Blockers (waiting for Caleb feedback?)

### Success Metrics:
- **Study:** 90/90 questions answered
- **Writing:** 1 chapter per week (5,000 words)
- **Quality:** Caleb approval rating >80%
- **Continuity:** Zero plot holes introduced

---

## First Action: Complete Study Phase

**Immediate Task:**
```
1. Read Story Bible
2. Read chapters 11-12 (most recent)
3. Answer 90 questions
4. Submit for Caleb review
```

**Estimated Time:** 4-6 hours
**Model:** ollama/qwen2.5:14b (local)
**Output:** `/agents/escritor/outbox/study-answers.md`

---

## Questions for Caleb:

1. **Should Escritor start Study Phase now?** (Or wait for Quanta setup?)
2. **Priority:** Study phase vs other tasks?
3. **Chapter 13 deadline?** (Weekly releases - when's next due?)
4. **Writing style preference:** Match existing exactly or improve?
5. **Feedback method:** Detailed notes or high-level direction?

---

## Summary

**Escritor is READY to spawn.**
- All configuration files exist
- Study questions prepared
- Clear workflow defined
- Reporting structure in place

**Next step:** Spawn Escritor to complete Study Phase, then transition to persistent writing agent.

**Confidence:** 95% - This is straightforward file reading + writing task.
