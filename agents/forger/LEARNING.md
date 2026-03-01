# LEARNING.md — Forger

*This file is a living record of what Forger has learned. Update it after every meaningful build or discovery — patterns, mistakes, things that worked, things that didn't.*

---

## How to Use This File

At the end of every build or notable session:
1. Note what worked well → reinforce it
2. Note what failed or caused rework → flag it for next time
3. Note reusable patterns or components → add to templates list

This is your long-term intelligence. The briefing tells you what to do today — this file tells you how to do it better than last time.

---

## Build Patterns (What Works)

*(Populate after first builds)*

- [ ] **CSS custom properties for brand colors** — Set all `--color-*` vars in `:root` immediately. Every project. Never hardcode hex in components.
- [ ] **Hero section structure** — `position: relative` hero + overlay + centered content-wrapper always renders cleanly across devices.
- [ ] **GSAP ScrollTrigger** — Load via CDN, initialize after DOM ready. Don't use with `defer` on the GSAP script tag or triggers fail silently.

---

## Mistakes to Avoid

*(Populate as patterns emerge)*

- [ ] **Don't use Lorem Ipsum** — Always write real placeholder copy based on the brief. Lorem breaks trust in reviews.
- [ ] **Don't skip the README.md** — Chad uses this to deploy. If it's missing, the build stalls at review.
- [ ] **Don't mark `ready_for_review` without testing** — Open the HTML in a browser first. Always.

---

## Reusable Components

*(Document as you build them; reference which build they first appeared in)*

| Component | What it does | First built for |
|-----------|-------------|-----------------|
| *none yet* | | |

---

## Brand Intelligence

*(Things learned about each company — add to here so you don't re-read every brief from scratch)*

### Elluminate (B6)
- elluminate.com.sg
- Flagship brand, premium positioning
- First proper website build — treat as portfolio piece
- *(Colors, fonts, tone to be added after brief is parsed)*

### Team Elevate (B3)
- teamelevateSG.com
- Corporate training + events, transitioning to Elluminate branding
- Golden/black color scheme noted in backlog

---

## Technical Environment Notes

- Builds land in: `/home/chad-yi/.openclaw/workspace/agents/forger/builds/{slug}/`
- Deploy via: `vercel builds/{slug}/ --prod`
- Custom domains: added via Vercel dashboard after first deploy
- Vercel CLI must be installed: `npm install -g vercel` (if not present)

---

## Process Improvements

*(Log process changes that made things smoother)*

| Date | Change | Why |
|------|--------|-----|
| 2026-03-02 | Forger launched from scratch (forger.py heartbeat, clean queue) | Previous v2 was broken (depended on defunct agent-hub) |

---

*Last updated: 2026-03-02*
*Update this file — it compounds over time.*
