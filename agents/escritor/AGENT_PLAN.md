# Escritor Agent - Full Implementation Plan

## Agent Overview

**Name:** Escritor  
**Code:** A2  
**Role:** Story Agent - RE:UNITE Novel Writer  
**Parent:** CHAD_YI  
**Model:** ollama/qwen2.5:14b (local)  

**Mission:** Collaborate with Caleb to write RE:UNITE Chapter 13 and beyond (weekly chapters)

---

## Phase 1: Study Phase (Current - A2-13)

### Objective
Read and deeply understand RE:UNITE chapters 1-12 and Story Bible to prepare for collaborative writing.

### Tasks:
1. **Read Story Bible** (`/projects/A2-reunite/STORY-BIBLE-COMPLETE.md`)
   - World rules, magic system, character profiles
   - Setting details (Runevia prison)
   - Plot arcs and unresolved threads

2. **Read Chapters 1-12** (`/temp-reunite/*.docx`)
   - Start with chapters 11-12 (most recent)
   - Work backwards to understand continuity
   - Note Caleb's writing style, voice, pacing

3. **Study Questions** (Optional but recommended)
   - 90 questions in `/agents/escritor/inbox/study-questions.md`
   - Answer key questions to verify understanding
   - Save answers to `/agents/escritor/outbox/study-answers.md`

### Success Criteria:
- Can summarize main plot arcs
- Knows character voices and motivations
- Understands magic system (Ether vs mana)
- Familiar with Caleb's writing style
- Ready to write in Caleb's voice

### Duration: 4-6 hours

---

## Phase 2: Collaborative Writing (A2-14 and beyond)

### Weekly Workflow

#### Monday: Planning Session with Caleb
1. **Review previous chapter ending**
   - What cliffhanger or plot point to resolve?
   - Character positions and emotional states

2. **Caleb provides direction**
   - Key scenes to include
   - Character beats
   - Plot developments
   - Word count target (3,000-5,000 words)

3. **Escritor drafts outline**
   - 3-5 scene structure
   - Send to Caleb for approval
   - Revise based on feedback

#### Tuesday-Wednesday: First Draft
1. **Write first draft**
   - Follow approved outline
   - Maintain Caleb's voice and style
   - Include dialogue, action, description
   - Hit word count target

2. **Save to outbox**
   - `/agents/escritor/outbox/chapter-XX-draft-v1.md`
   - Report progress to Helios

#### Thursday: Caleb Review
1. **Caleb reviews draft**
   - Provides detailed feedback
   - Notes what works, what doesn't
   - Suggests revisions

2. **Escritor receives feedback**
   - Via message bus or direct
   - Acknowledges notes

#### Friday: Revision
1. **Revise based on feedback**
   - Address all Caleb's notes
   - Polish prose
   - Fix continuity issues

2. **Submit final draft**
   - `/agents/escuritor/outbox/chapter-XX-final.md`
   - Mark complete

#### Weekend: Publishing (Caleb handles)
- Caleb formats and publishes to Google Drive
- Escritor rests/reads for next week

---

## Agent Architecture

### File Structure
```
/agents/escritor/
├── SOUL.md                    # Who Escritor is (✅ exists)
├── SKILL.md                   # How to write (✅ exists)
├── MEMORY.md                  # Story continuity (✅ exists)
├── current-task.md            # Current assignment (✅ exists)
├── AGENT_STATE.json           # Persistent state (✅ exists)
├── IMPLEMENTATION_PLAN.md     # This file
│
├── inbox/                     # Messages TO Escritor
│   ├── study-questions.md     # 90 questions (✅ exists)
│   ├── caleb-feedback/        # Feedback on drafts
│   └── outline-requests/      # Caleb's chapter direction
│
├── outbox/                    # Escritor's outputs
│   ├── study-answers.md       # Study phase answers
│   ├── outlines/              # Chapter outlines
│   ├── drafts/                # Chapter drafts (v1, v2, etc.)
│   └── final/                 # Final chapters
│
└── projects/
    └── A2-reunite/
        ├── story-bible-notes.md    # Escritor's notes on Story Bible
        ├── character-voices.md     # Voice guides for each character
        ├── continuity-tracker.md   # Plot threads to resolve
        └── style-guide.md          # Caleb's writing patterns
```

### Memory Files (Escritor maintains)

**character-voices.md**
- Ryfel: SEAL mindset, tactical, protective
- Kriscila: Determined, 3-year promise, magic user
- Dialogue patterns for each character

**continuity-tracker.md**
- Unresolved plot threads
- Character arcs in progress
- Magic system rules established
- Callbacks to remember

**style-guide.md**
- Caleb's sentence structure patterns
- Pacing preferences
- Dialogue formatting
- Chapter structure (hooks, cliffhangers)

---

## Communication Protocol

### Helios → Escritor (Every 15 minutes)
```
"Escritor, status check:
- Study phase: X% complete
- Current chapter: Y words written
- Blockers: [none/waiting for Caleb feedback/technical issue]
- ETA: Z hours"
```

### Escritor → Helios
```
Report:
- Progress update
- Any blockers
- ETA for current milestone
```

### Escritor → CHAD_YI
- Daily progress summary (evening)
- Draft submissions
- Questions needing Caleb's input

### Escritor → Caleb (via CHAD_YI)
- Chapter outlines for approval
- Draft chapters for review
- Questions about direction

---

## Running Escritor

### Option 1: File-Based (Study Phase)
**How it works:**
- Escritor runs once to complete study
- Reads files, writes answers
- Reports completion
- Stops when done

**Command:**
```bash
sessions_spawn(
    agentId="ollama/qwen2.5:14b",
    task="You are Escritor. Complete A2-13 Study Phase. Read Story Bible and chapters 1-12. Optionally answer study questions. Report progress every 30 minutes.",
    timeoutSeconds=21600  # 6 hours
)
```

### Option 2: Persistent Session (Writing Phase)
**How it works:**
- Escritor runs continuously
- Self-motivated workflow
- Checks for Caleb feedback regularly
- Writes autonomously within guidelines

**Command:**
```bash
sessions_spawn(
    agentId="ollama/qwen2.5:14b",
    task="You are Escritor, persistent story agent for RE:UNITE. Weekly workflow: Monday plan with Caleb, Tue-Wed write draft, Thu review, Fri revise. Check inbox every hour for feedback. Report to Helios every 15 min.",
    timeoutSeconds=604800  # 7 days
)
```

### Recommended: Hybrid

**Phase 1 (Now):** File-based study
- Spawn once for 4-6 hours
- Complete understanding phase
- Caleb reviews answers
- Takes 1-2 days

**Phase 2 (After approval):** Persistent writing
- Spawn as continuous agent
- Weekly chapter cycle
- Ongoing collaboration

---

## Success Metrics

### Study Phase (A2-13)
| Metric | Target | Measurement |
|--------|--------|-------------|
| Story Bible read | 100% | Can summarize key points |
| Chapters 1-12 read | 100% | Understands plot arcs |
| Study questions | 70%+ answered | Demonstrates comprehension |
| Caleb approval | Yes | Review of answers |

### Writing Phase (A2-14+)
| Metric | Target | Measurement |
|--------|--------|-------------|
| Weekly chapter | 1 per week | Delivered by Friday |
| Word count | 3,000-5,000 | Per chapter |
| Caleb approval | 80%+ | Feedback iterations |
| Continuity errors | 0 | No plot holes |
| Style match | High | Sounds like Caleb |

---

## Error Handling

### If Escritor gets stuck:
1. **Can't understand Story Bible** → Ask Caleb specific questions
2. **Writer's block** → Take break, re-read previous chapter
3. **Caleb feedback unclear** → Ask for clarification
4. **Technical issue (file not found)** → Report to CHAD_YI

### If quality drops:
1. **More review cycles** → Caleb provides detailed notes
2. **Re-read previous chapters** → Refresh voice memory
3. **Smaller sections** → Draft scene-by-scene

---

## Questions for Caleb

1. **Study Phase:** Start now or wait for Quanta setup complete?
2. **Chapter 13 deadline:** When is next chapter due?
3. **Feedback style:** Detailed line edits or high-level direction?
4. **Revision rounds:** How many drafts per chapter typical?
5. **Publishing:** Caleb handles Google Drive upload?
6. **Word count:** Target per chapter (3k? 5k? flexible)?

---

## Technical Requirements

### For Study Phase:
- **Model:** ollama/qwen2.5:14b (local)
- **Memory:** 16GB RAM available
- **Time:** 4-6 hours
- **Files:** Read .md and .docx

### For Writing Phase:
- **Model:** Same (ollama/qwen2.5:14b)
- **Runtime:** 24/7 persistent
- **Storage:** Write to outbox/
- **Reporting:** Every 15 min to Helios

---

## Next Steps

### To Start Study Phase:
```bash
1. Spawn Escritor with study task
2. He reads Story Bible + chapters 1-12
3. He answers study questions (optional)
4. Submits completion report
5. Caleb reviews
6. Approve → move to writing phase
```

### To Start Writing Phase:
```bash
1. Spawn Escritor as persistent agent
2. He enters weekly workflow
3. Monday: Plan with Caleb
4. Tue-Fri: Write and revise
5. Friday: Submit final chapter
6. Repeat weekly
```

---

## Summary

**Escritor is ready to spawn.** All configuration exists. Two-phase approach:

1. **Study Phase (A2-13):** File-based, 4-6 hours, understand RE:UNITE
2. **Writing Phase (A2-14+):** Persistent, weekly chapters, collaborate with Caleb

**Confidence:** 90% - Clear workflow, defined outputs, manageable scope.

**Ready when you say go.**
