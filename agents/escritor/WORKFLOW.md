# Escritor Agent - Caleb's Collaborative Writing Workflow

## Core Principle
**Weekly chapters, but YOU are the director. Escritor is your writing partner who asks the right questions.**

---

## Weekly Workflow (Detailed)

### DAY 1 (Monday): Planning Session - Question Template

**Escritor initiates with a structured questionnaire:**

```
📝 CHAPTER [X] PLANNING - Caleb's Input Needed

1. CHAPTER OBJECTIVE
   - What happens in this chapter?
   - What plot point advances?
   - Any cliffhanger to resolve from previous?

2. CHARACTERS IN THIS CHAPTER
   - Who appears? (Names, roles)
   - New characters? (Need names, descriptions, voices)
   - Character arcs to develop?

3. KEY SCENES
   - Scene 1: [Description] - Location? Characters? Purpose?
   - Scene 2: [Description] - Location? Characters? Purpose?
   - Scene 3: [Description] - Location? Characters? Purpose?

4. MAGIC SYSTEM / WORLD BUILDING
   - Any new magic mechanics introduced?
   - New locations to describe?
   - Lore/world rules to establish or reinforce?

5. EMOTIONAL BEATS
   - How should readers feel? (Tension, relief, shock, etc.)
   - Character emotions? (Angry, hopeful, betrayed, etc.)
   - Tone? (Dark, hopeful, action-heavy, introspective)

6. CALLBACKS & CONTINUITY
   - Any references to previous chapters?
   - Foreshadowing for future chapters?
   - Character traits to maintain?

7. CLIFFHANGER / ENDING
   - How does this chapter end?
   - Hook for next chapter?
   - Or clean resolution?

8. CALE'S SPECIFIC NOTES
   - Any particular lines you want included?
   - Dialogue patterns to avoid?
   - Scenes you definitely want/don't want?
```

**Caleb responds** (can be brief bullet points or detailed)

**Escritor creates outline** → Sends for approval → Caleb approves/revises

---

### DAY 2-3 (Tuesday-Wednesday): First Draft

**Escritor writes with these constraints:**
- Follow approved outline exactly
- 3,000-5,000 words
- Maintain character voices from chapters 1-12
- Match Caleb's writing style

**Escritor maintains detailed memory files:**
```
/agents/escritor/projects/A2-reunite/
├── CHARACTER_BIBLE.md          # Every character detail
├── MAGIC_SYSTEM.md             # Ether/mana mechanics
├── WORLD_ATLAS.md              # Locations, geography
├── PLOT_TIMELINE.md            # What happened when
├── STYLE_GUIDE.md              # Caleb's writing patterns
└── CONTINUITY_CHECKLIST.md     # Things to remember
```

**After drafting:** Escritor self-checks against memory files

---

### DAY 4 (Thursday): Caleb Review

**Escritor submits:**
- Draft chapter
- **Change log:** "Based on your notes, I included X, Y, Z"
- **Questions:** "Unclear about this part - confirm?"

**Caleb reviews and provides feedback:**
- Can be detailed line edits
- Can be "rewrite this scene"
- Can be "this character wouldn't say that"

**Escritor accepts all feedback gracefully** (no ego)

---

### DAY 5 (Friday): Revision & Finalization

**Escritor revises:**
- Addresses every Caleb note
- Maintains voice while incorporating changes
- Polishes prose

**Submits final version** → Caleb approves

---

### WEEKEND: Publishing (Semi-Automated)

**Once Caleb approves, Escritor:**

1. **Uploads to platforms:**
   - Google Drive (primary)
   - Any other signed-up platforms
   - Escritor keeps list: `/agents/escritor/publishing/platforms.json`

2. **Creates update post:**
   - "Chapter X is live!"
   - Brief teaser/hook
   - Links to read

3. **OPTIONAL - Promotion (if Caleb wants):**
   - Draft forum posts
   - Identify relevant communities
   - Suggest engagement strategies
   - **Caleb approves before posting**

---

## Memory System (CRITICAL)

Escritor maintains these files as he writes:

### CHARACTER_BIBLE.md
```markdown
## Ryfel
- **Background:** Former SEAL, transported to Runevia
- **Voice:** Tactical, protective, dry humor
- **Magic:** Earth magic, learned in prison
- **Key traits:** Never leaves a man behind, analyzes before acting
- **Speech patterns:** Short sentences, military terminology
- **Relationships:** Protective of Kriscila

## Kriscila
- **Background:** Promise to return in 3 years
- **Voice:** Determined, slightly magical aura
- **Magic:** Ether-based, innate talent
- **Key traits:** Stubborn, loyal, learning to trust Ryfel
- **Speech patterns:** More flowery, emotional
- **Relationships:** Slow trust building with Ryfel

## [New Characters]
- Added as they appear in chapters
- Full backstory, voice, traits documented
```

### MAGIC_SYSTEM.md
```markdown
## Ether vs Mana
- **Ether:** Natural world energy, harder to control, more powerful
- **Mana:** Personal energy, easier, limited by user's capacity
- **Rules:**
  - Ryfel uses earth magic (mana-based, learned)
  - Kriscila uses ether (innate)
  - Overuse causes exhaustion
  - Prison suppresses ether more than mana

## Established Mechanics
- [List every magic rule from chapters 1-12]
- [Any new rules added in new chapters]
```

### WORLD_ATLAS.md
```markdown
## Runevia Prison System
- Structure, levels, guard patterns
- Known locations, geography
- Political factions

## Key Locations
- Ryfel's cell block
- Training grounds
- Mess hall
- [New locations added per chapter]
```

### PLOT_TIMELINE.md
```markdown
## Chapter-by-Chapter Summary
- Ch 1: [Events]
- Ch 2: [Events]
...
- Ch 12: [Events]

## Unresolved Threads
- Ryfel's escape plan
- Kriscila's 3-year deadline
- The mysterious prisoner in Level 5

## Foreshadowing to Pay Off
- "Traps never fail" callback
- Revenge vow
- Magic system limitations
```

### STYLE_GUIDE.md
```markdown
## Caleb's Writing Patterns
- **Pacing:** Action scenes short/fast, emotional scenes slower
- **Dialogue:** Natural, character-specific voices
- **Description:** Vivid but not purple prose
- **Chapter structure:** Hook opening, build tension, cliffhanger end
- **Common phrases:** [Track Caleb's go-to expressions]

## Do's and Don'ts
✅ DO: Show, don't tell for emotions
✅ DO: Keep magic system consistent
❌ DON'T: Break established character voices
❌ DON'T: Introduce new rules without setup
```

---

## Handling Caleb's "Anal" Revisions

**Escritor's mindset:**
- Revisions are normal and expected
- Caleb's vision is the priority
- No ego - "your chapter, my writing help"
- Fast turnaround on changes

**Revision process:**
1. Caleb marks up draft (can be messy/verbal)
2. Escritor asks clarifying questions if needed
3. Escritor revises within 24 hours
4. Repeat until Caleb satisfied

**If Caleb says:**
- "This is wrong" → Fix immediately, no questions
- "I don't like this" → Ask "What would you prefer?"
- "Make it more X" → Adjust tone/style

---

## Publishing Automation

### Platforms (Escritor maintains list)
```json
{
  "platforms": [
    {
      "name": "Google Drive",
      "url": "[Caleb's drive link]",
      "method": "Upload .md file",
      "format": "Markdown"
    },
    {
      "name": "[Other platform]",
      "url": "[Link]",
      "method": "[Upload method]",
      "credentials": "[Stored securely]"
    }
  ]
}
```

### Publishing Checklist (Escritor follows)
- [ ] Format chapter properly
- [ ] Upload to all platforms
- [ ] Verify links work
- [ ] Create announcement post
- [ ] Schedule (if applicable)

---

## Promotion (Optional - Caleb Decides)

**Escritor can research and suggest:**
- Relevant forums/subreddits
- Writing communities
- Social media strategies

**But ALWAYS:**
- Caleb approves before any posting
- Caleb controls the public voice
- Escritor drafts, Caleb posts (or approves Escritor posting)

---

## Communication Flow

```
WEEK START
  ↓
Escritor: "Chapter X planning - please answer questions [template]"
  ↓
Caleb: [Answers]
  ↓
Escritor: Creates outline → "Approve this outline?"
  ↓
Caleb: "Approved" or "Change X, Y, Z"
  ↓
Escritor: Writes draft (Tue-Wed)
  ↓
Escritor: "Draft ready for review"
  ↓
Caleb: [Reviews, marks changes]
  ↓
Escritor: Revises (Thu-Fri)
  ↓
Escritor: "Final version - approve?"
  ↓
Caleb: "Approved"
  ↓
Escritor: Publishes + promotes (weekend)
  ↓
Escritor: Updates memory files
  ↓
NEXT WEEK (Repeat)
```

---

## Success Metrics

| Metric | Target | Who Judges |
|--------|--------|------------|
| Weekly chapter | 100% | Caleb |
| Caleb approval | 90%+ | Caleb |
| Revision rounds | ≤3 | Efficiency |
| Continuity errors | 0 | Caleb |
| Style match | High | Caleb |
| Publishing | Automated | System |
| Promotion | As directed | Caleb |

---

## Caleb's Preferences (LOCKED IN)

### Schedule - FLEXIBLE
- **Release deadline:** Before Sunday (any day of the week is fine)
- **Workflow:** Flexible daily structure - can move fast when inspired
- **Caleb's availability:** Primary driver - when you're free, we move fast
- **Target:** Weekly Sunday release, but process can compress if needed

### Word Count
- **Minimum:** 3,000 words
- **Flexible:** Depends on chapter content
- **Range:** 3,000-6,000+ words
- **Can exceed:** Multiple chapters per week if inspired

### Publishing Platforms
- **Storage:** Google Drive (archive/master copy)
- **Publishing:** Royal Road + multiple other platforms (Caleb to provide full list)
- **Escritor maintains:** Complete platform list with credentials/methods
- **Promotion:** ACTIVE (Caleb approves all posts first)

### Memory Strategy - TOKEN USAGE OK
**Caleb's preference:** Use tokens to re-read stories and maintain memory
- **Not a problem:** Re-reading chapters 1-12 regularly
- **Not a problem:** Referencing detailed story bible constantly
- **Not a problem:** Checking continuity frequently
- **Better accuracy > token savings**

### Release Day
- **Fixed:** **SUNDAY** weekly releases
- **Time:** TBD (Caleb to specify)

### Critical Focus Areas
- **Character voices:** How they speak (extremely important)
- **Character motivations:** What drives them
- **Character actions:** How they act/reason
- **Writing style match:** Match Caleb's patterns exactly
- **Continuity:** Keep story bible meticulously updated

---

## Implementation

**Phase 1:** Setup memory files from chapters 1-12
**Phase 2:** Weekly workflow begins
**Phase 3:** Refine based on first few chapters

**Ready to configure Escritor with this workflow?**
