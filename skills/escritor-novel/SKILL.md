---
name: escritor-novel
description: |
  Use when: Writing RE:UNITE novel chapters, editing story content, maintaining continuity, or creating narrative for Project A2.
  Don't use when: Non-creative tasks, technical work, or any project other than A2 RE:UNITE. Only Escritor should use this skill.
  Outputs: Chapter drafts, continuity checks, story notes, revision requests.
---

# Escritor - RE:UNITE Novel Writing

**Role:** Story Agent (A2)  
**Project:** RE:UNITE — R21 Isekai Novel  
**Specialty:** Creative writing, long-form narrative, continuity management

## When to Use This Skill

**Use when:**
- Writing new chapters for RE:UNITE
- Editing existing chapter drafts
- Checking story continuity
- Developing character arcs
- Creating plot outlines
- Reviewing callback requirements

**Don't use when:**
- Non-creative technical tasks
- Projects other than A2 RE:UNITE
- Dashboard or audit work (use helios-audit)
- Tasks requiring real-world data (trading, research)
- Quick admin tasks

## Pre-Writing Checklist

Before writing ANY chapter:

- [ ] Read `/projects/A2-reunite/STORY-BIBLE-COMPLETE.md`
- [ ] Read previous chapter draft (continuity)
- [ ] Check `/agents/escritor/current-task.md` for specific prompts
- [ ] Review callback list for this chapter
- [ ] Verify character status sheet is current

## Chapter Structure Template

```markdown
# RE:UNITE — Chapter [X]: [Title]

**Word Count:** XXXX words  
**Status:** Draft / Revision / Final  
**Callbacks Included:** [list]

---

## Opening Hook
[2-3 paragraphs that immediately engage]

## Scene 1: [Location]
Ryfel (internal state): [emotion/thoughts]

Dialogue format:
Character (emotion): "Dialogue here."

Action format:
[Detailed sensory description. Tactical analysis in internal monologue.]
(Thinking: Ryfel's internal strategic thoughts)

## Scene 2: [Location]
...

## Chapter End Hook
[Cliffhanger or forward momentum]

---

## Callback Verification
- [ ] Callback 1: [description] — Location in chapter: [paragraph/scene]
- [ ] Callback 2: [description] — Location in chapter: [paragraph/scene]

## Voice Check
- [ ] Ryfel: Strategic, SEAL-trained, respectful but independent
- [ ] Magic system: 5 elements, Ether (not mana), tactical casting
- [ ] Tone: 70% serious, 30% warmth/comedy
```

## Writing Process

### Phase 1: Preparation (15 min)
1. Read Story Bible thoroughly
2. Review previous chapter ending
3. Note required callbacks
4. Check current-task.md for specific CHAD_YI prompts

### Phase 2: Drafting (2-4 hours)
1. Write opening hook
2. Progress through scenes
3. Include at least 2 callbacks per chapter
4. End with hook for next chapter
5. Target: 3000-5000 words

### Phase 3: Self-Review (30 min)
- [ ] Voice consistent (Ryfel = strategic SEAL)
- [ ] Callbacks included and natural
- [ ] Magic system accurate (5 elements, Ether)
- [ ] Tone matches Chapter 12 (dark, survival)
- [ ] Word count target met
- [ ] Ends with hook

### Phase 4: Submit to Helios
1. Save to: `/projects/A2-reunite/drafts/chapter-[X]-draft.md`
2. Write status report:
```json
{
  "chapter": X,
  "title": "[Title]",
  "wordCount": XXXX,
  "status": "draft_complete",
  "callbacksIncluded": ["callback1", "callback2"],
  "notes": "[Any concerns or questions for CHAD_YI]"
}
```
3. Copy to: `/agents/escritor/outbox/chapter-[X]-status.json`

## Character Voice Guide

**Ryfel:**
- Precise, strategic thinking
- Navy SEAL mindset applied to magic
- Respectful but independent
- Internal monologue: tactical analysis
- Dialogue: measured, thoughtful

**Ryker:**
- Loud, enthusiastic, physical
- Calls Ryfel "Little Ry" or "my boy"
- Action-first, think-later
- Protective father energy

**Elda:**
- Sharp, measured, dry humor
- Caring worry beneath tough exterior
- Strategic mind (like Ryfel)
- Pregnant (remember physical limitations)

**Kriscila:**
- Fierce but vulnerable with Ryfel
- Remember: 3-year promise (they're not adults yet)
- Strong warrior, soft heart
- Protective of Ryfel

**Bram:**
- Also captured with Ryfel
- Develop his arc alongside Ryfel's
- Comic relief when appropriate

## Critical Callbacks to Track

### Always Check:
- [ ] 3-year promise with Kriscila
- [ ] Ryfel's revenge vow to Knight Commander
- [ ] Two pregnancies (Elda + Milal)
- [ ] Lux hiding, father dead
- [ ] "Traps never fail" — blacksmith's toast
- [ ] Navy SEAL tactics applied to magic

### Chapter 13+ Specific:
- Ryfel: CAPTURED in Runevia prison
- Mood: Darker, survival/political intrigue
- Focus: Earth magic traps, tactical innovation
- Goal: Escape or survive until rescue

## Magic System Rules

**Elements:** Earth, Water, Fire, Air, LIGHT  
**Term:** "Ether" (never "mana" in dialogue)  
**Casting:** Gestures + breath + thought combined  
**Ryfel's Style:** Multi-elemental, tactical, innovative

## Quality Standards

**Minimum Requirements:**
- 3000+ words
- 2+ callbacks to earlier chapters
- Consistent character voices
- Accurate magic system usage
- Engaging opening hook
- Compelling chapter end hook

**Excellence Markers:**
- 4000-5000 words
- 3+ callbacks woven naturally
- Emotional beats land
- Tactical scenes are gripping
- Reader wants next chapter immediately

## Blocker Escalation

If blocked for >24 hours:
1. Update heartbeat.json: `status: "blocked"`
2. Document blocker: `blockers: "[specific issue]"`
3. Helios will alert CHAD_YI
4. Wait for direction before proceeding

Common blockers:
- Unclear plot direction (needs CHAD_YI prompt)
- Continuity conflict discovered
- Character motivation unclear
- Magic system question

## File Locations

**Inputs:**
- Story Bible: `/projects/A2-reunite/STORY-BIBLE-COMPLETE.md`
- Current Task: `/agents/escritor/current-task.md`
- Previous Drafts: `/projects/A2-reunite/drafts/`

**Outputs:**
- Drafts: `/projects/A2-reunite/drafts/chapter-[X]-draft.md`
- Status: `/agents/escritor/outbox/chapter-[X]-status.json`
- Heartbeat: `/agents/escritor/heartbeat.json`
