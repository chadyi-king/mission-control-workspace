

---

## Memory Strategy - How Escritor Remembers

### Core Principle
**Better accuracy > Token savings.** Re-read source material as needed.

### Regular Refresh Cycle
```
Every Monday (or planning day):
  ↓
Re-read Story Bible (full)
  ↓
Re-read chapters 11-12 (most recent)
  ↓
Re-read specific chapters if needed for continuity
```

### Memory Files (Escritor Maintains)
**These are LIVING documents - updated after every chapter:**

```markdown
CHARACTER_BIBLE.md
├── Updated after every chapter
├── New characters added immediately
├── Voice notes refined based on Caleb feedback
└── Before writing: Re-read relevant character sections

MAGIC_SYSTEM.md
├── Magic rules updated if new mechanics introduced
├── Limitations documented
└── Before writing: Review if magic used in chapter

WORLD_ATLAS.md
├── New locations added per chapter
├── Descriptions refined
└── Before writing: Check setting details

PLOT_TIMELINE.md
├── Every chapter summary added
├── Foreshadowing tracker updated
└── Before writing: Check unresolved threads

STYLE_GUIDE.md
├── Caleb's patterns documented
├── Updated based on Caleb's revision notes
└── Before writing: Review voice patterns
```

### Token Usage Strategy
**Caleb's preference: USE TOKENS FREELY**

**Before writing each chapter:**
1. **Read Story Bible** (~5k tokens) - REFRESH world knowledge
2. **Read chapters 11-12** (~10k tokens) - Recent continuity
3. **Read specific references** (~2-5k tokens) - If needed
4. **Reference memory files** (~3k tokens) - Character voices, etc.

**Total per chapter:** ~20k tokens (acceptable for quality)

**Why this works:**
- Ensures continuity
- Maintains voice consistency
- Catches details human might miss
- Better than relying on potentially stale memory files

---

## Communication - How Escritor Talks to CHAD_YI

### File-Based Communication (Primary)

**CHAD_YI ↔ Escritor via files:**

```
/agents/message-bus/chad-yi-to-escritor/pending/
  └── [timestamp]-instructions.md
      
/agents/message-bus/escritor-to-chad-yi/pending/
  └── [timestamp]-draft-chapter-13.md
  └── [timestamp]-questions.md
  └── [timestamp]-status-update.md
```

**Pattern:**
1. CHAD_YI writes instructions → Escritor inbox
2. Escritor reads → Completes work
3. Escritor writes response → CHAD_YI inbox
4. CHAD_YI reviews → Next cycle

### Direct Messages (Urgent)

**For urgent issues:**
- Escritor sends to `helios-to-chad-yi` message bus
- Helios forwards immediately
- CHAD_YI responds

**Urgent examples:**
- "Can't find Chapter 11 file"
- "Caleb's feedback unclear - need clarification"
- "Technical error - can't save file"

---

## Helios Integration - Reminders & Poking

### Helios → Escritor (Every 15 Minutes)

**Standard poke:**
```
Helios: "Escritor, status check for A2-13:
- Study phase: X% complete?
- Any blockers?
- ETA for completion?
- Need CHAD_YI assistance?"

Escritor: "Status: 60% complete
Blockers: None
ETA: 2 more hours
Action: Continuing reading Chapter 10"
```

**During Writing Phase:**
```
Helios: "Escritor, Chapter 14 status:
- Draft progress: X words?
- Day of week: [Day]
- Days until Sunday: Y
- On track for release?
- Blockers: [none/waiting for Caleb feedback/other]"

Escritor: "Progress: 2,400 words
Day: Wednesday
Days to Sunday: 4
Status: On track
Blockers: None - drafting scene 3"
```

### Helios Alerts (Triggers)

**Auto-alert to CHAD_YI if:**
- Escritor idle >2 hours during writing phase
- Missed internal deadline (Thursday draft)
- Escritor reports "waiting for Caleb feedback" >24 hours
- Technical error preventing work

**Escritor → Helios (On completion):**
```
"Task A2-13 complete. Study phase finished.
Ready for Caleb review.
Next: A2-14 Chapter 13 writing"
```

---

## Summary

**Escritor's Operation:**
1. **Memory:** Re-reads source material regularly (tokens OK)
2. **Writes:** Maintains detailed story bible
3. **Communicates:** Via file-based message bus
4. **Reports:** Every 15 min to Helios
5. **Quality:** Better accuracy than token savings
6. **Schedule:** Flexible, release by Sunday

**Ready to spawn.**
