# current-task.md — Forger
*Read this first. Update before ending every session.*

---

## Status (as of 2026-03-09)
**Forger has NOT been launched yet.** Identity stack is now complete.
Service is installed but NOT started — waiting for first active session.

---

## Build Queue (7 pending)

| Priority | Slug | Company | Notes |
|----------|------|---------|-------|
| 1 | `task--b6-elluminate-website` | Elluminate (B6) | **START HERE** — flagship brand |
| 2 | `task--rebuild-elluminate-sg-website` | Elluminate (B6) | Rebuild brief — check overlap with #1 |
| 3 | `task--complete-elluminate-sg-website---all-pages` | Elluminate (B6) | All pages brief |
| 4 | `b6-elluminate-visual-reference` | Elluminate (B6) | Visual reference only |
| 5 | `forge---design-brief-template` | Template | Design brief template |
| 6 | `b3---b6-website-deployment-brief` | B3+B6 Deploy | Deployment instructions |
| 7 | `task--create-hero-banner-visual` | Hero Banner | Visual asset |

**Note:** Items 1, 2, 3 all appear to be Elluminate — read all 3 briefs first and
consolidate into a single build plan before starting.

---

## Blockers
- None currently known
- If Lovable export is needed: manual browser login required (CLI unreliable)
- Claude Sonnet API key — check `.secrets/` folder before coding session

---

## What to Do at Session Start

1. Read all 3 Elluminate briefs from `inbox/`
2. Look for any `cerebronn-plan-*.md` in `inbox/` — Cerebronn may have planned this already
3. Consolidate brief into a single build plan
4. Choose: Lovable shell → enhance, OR build from scratch (see SOUL.md decision tree)
5. Start with homepage. Get it 90%+ before next page.
6. Update this file and heartbeat.json at session end.

---

## Last Session
- **Date:** 2026-03-02
- **What happened:** Forger service installed. 4 briefs detected and queued. No builds started.
- **2026-03-09 update:** Identity stack completed (SOUL, SKILL, LEARNING, current-task + openclaw.json wired).
- **Waiting on:** First OpenClaw session with Forger to start the Elluminate build.

---

## File Paths Quick Reference
```
Inbox:    /home/chad-yi/.openclaw/workspace/agents/forger/inbox/
Builds:   /home/chad-yi/.openclaw/workspace/agents/forger/builds/
Outbox:   /home/chad-yi/.openclaw/workspace/agents/forger/outbox/
Queue:    /home/chad-yi/.openclaw/workspace/agents/forger/memory/build-queue.json
Secrets:  /home/chad-yi/.openclaw/workspace/agents/forger/.secrets/
```
