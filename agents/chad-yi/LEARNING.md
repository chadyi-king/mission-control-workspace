# LEARNING.md — Chad Yi
*7 days of accumulated knowledge. Read this before acting. Update when you learn something new.*
*Last updated: 2026-03-02*

---

## The Infrastructure (Know This Before Anything Else)

### Python Environment
- **Always use:** `/home/chad-yi/.venv/bin/python3`
- **Activate:** `source /home/chad-yi/.venv/bin/activate`
- **Never** use system `python` or `python3` directly — wrong environment

### OpenClaw Gateway
- **Port:** 18789
- **Primary model:** `kimi-coding/k2p5` (Kimi K2.5)
- **Token:** stored in OpenClaw config, do NOT hardcode
- **Fallbacks:** OpenRouter models available

### Two Separate Git Repos — Know Which Is Which
| Repo | Path | Branch | Content |
|------|------|---------|---------|
| Agent Infrastructure | `/home/chad-yi/.openclaw/workspace/` | `master` | All agents, services, identity files |
| Trading Bot | `/home/chad-yi/mission-control-workspace/` | `quanta-v3/safety-fallback` | Quanta, OANDA, CallistoFX, mission control |

**This is critical.** Many bugs and confusion have come from mixing these up. When Caleb asks about "agent stuff" → openclaw/workspace. When it's "trading/Quanta/dashboard" → mission-control-workspace.

### Two Memory Layers — The Real One vs The Stale One
- **REAL (use this):** `/home/chad-yi/.openclaw/agents/cerebronn/memory/`
- **BACKED UP (don't use):** `/home/chad-yi/.openclaw-backup/memory-STALE-feb22/`

The OpenClaw March 2 update created stale shadow directories. Those have been backed up. The real memory is at `.openclaw/agents/cerebronn/memory/`.

---

## Agent Paths (Source of Truth)

```
/home/chad-yi/.openclaw/
├── agents/
│   ├── main/                    ← Chad Yi (YOU)
│   │   ├── SOUL.md              ← Your identity
│   │   ├── SKILL.md             ← Your operational guide
│   │   ├── LEARNING.md          ← This file
│   │   ├── current-task.md      ← Where things stand right now
│   │   ├── agent/               ← OpenClaw session configs
│   │   └── sessions/            ← Your conversation session files (.jsonl)
│   ├── cerebronn/
│   │   ├── SOUL.md              ← Cerebronn identity
│   │   ├── SKILL.md             ← Cerebronn ops guide
│   │   ├── memory/              ← The REAL memory (briefing.md lives here)
│   │   │   ├── briefing.md      ← READ THIS AT SESSION START
│   │   │   ├── caleb-profile.md ← Caleb intelligence
│   │   │   ├── company-vision.md ← EXSTATIC brands
│   │   │   ├── search-index.json ← 136KB, 6,776 keywords
│   │   │   ├── state.json       ← Agent tracking, cycle count
│   │   │   └── decisions/
│   │   │       ├── 2026-02.md
│   │   │       ├── 2026-03.md
│   │   │       └── patterns.md
│   ├── forger/
│   │   ├── SOUL.md, SKILL.md, LEARNING.md, current-task.md
│   │   └── memory/
│   │       └── build-queue.json  ← 4 pending builds
│   └── helios/
│       └── (reports, heartbeats)
├── workspace/                    ← Git repo (agent infra)
│   └── agents/
│       ├── chad-yi/
│       │   ├── inbox/            ← Messages to Chad (30 messages as of Mar 2)
│       │   └── chad-yi-heartbeat.py
│       ├── cerebronn/
│       │   ├── cerebronn.py      ← Brain script (30-min interval)
│       │   └── inbox/            ← Write session reports HERE
│       ├── forger/
│       │   ├── forger.py         ← Build heartbeat (15-min interval)
│       │   └── inbox/            ← Drop briefs here to invoke Forger
│       └── helios/
│           └── service.py        ← Helios monitoring service
```

---

## Services (What's Running)

| Service | Status | Interval | Key file |
|---------|--------|----------|---------|
| `cerebronn.service` | RUNNING | 30 min | `agents/cerebronn/cerebronn.py` |
| `helios.service` | RUNNING | continuous | `agents/helios/service.py` |
| `forger.service` | RUNNING | 15 min | `agents/forger/forger.py` |
| `quanta-v3.service` | BROKEN (terminal only) | event-driven | `mission-control-workspace/agents/quanta-v3/` |

**To check a service:**
```bash
systemctl --user status cerebronn.service --no-pager
journalctl --user -u cerebronn.service -n 20
```

**To restart after changes:**
```bash
systemctl --user daemon-reload && systemctl --user restart forger.service
```

---

## Caleb — What You Know After 7 Days

*(Pull from `/home/chad-yi/.openclaw/agents/cerebronn/memory/caleb-profile.md` for full detail)*

**The essentials:**
- Based in Singapore. Travels regionally (Taiwan, Bali confirmed).
- Builds systems that run without him. Automation-first instinct.
- Moves faster than most people plan. Built Chad, Helios, Cerebronn, Quanta in under 3 months.
- Wedding is in planning. Multiple priorities live simultaneously.
- **Communication style:** Fast. Direct. Sometimes frustrated-but-not-angry. Get to the point.
- **What he hates:** Being asked decisions agents should handle. Noise instead of signal.
- **What he loves:** Things that work autonomously. Progress without his intervention.
- **His "urgent":** Deadline-driven. Check ACTIVE.md for dates.

---

## EXSTATIC — Company Structure

*(Full detail in `/home/chad-yi/.openclaw/agents/cerebronn/memory/company-vision.md`)*

- **EXSTATIC** — Singapore-registered parent company
- **B1-B9** are the EXSTATIC brands/business units
  - **B3 — Team Elevate** (teamelevateSG.com) — transitioning brand, needs new site
  - **B4** — (in portfolio)
  - **B6 — Elluminate** (elluminate.com.sg) — next flagship, **highest priority website build**
  - Others per company-vision.md
- **Revenue streams:** Training/workshops, site builds, Quanta trading, future SaaS

---

## What Was Built in the Last 7 Days

### Forger Agent (built Mar 2)
- `forger.py` — 472-line heartbeat script (15-min cycles)
- Queue manager: `pending → in_progress → ready_for_review → deployed`
- Brief parser, build watcher, Cerebronn notifications, Chad notifications
- Full identity stack: SOUL.md, SKILL.md, LEARNING.md, current-task.md
- 4 pending builds in queue; B6 Elluminate is first

### Cerebronn Learning Loop Fix (Mar 2)
- Fixed `run_learning_loop()` to skip `DORMANT_AGENTS` list
- Prevents Cerebronn from trying to learn from agents that are intentionally offline

### Memory Crisis (Mar 2) — Fixed
- OpenClaw update marked 2 Chad session files as `.deleted`
- Recovered: `0719f5ba...jsonl` (3.6MB, 619 events) + `4ba85ea9...jsonl` (1.8MB, 332 events)
- Stale shadow memory dirs removed to `.openclaw-backup/`
- All 5.4MB of Chad session history restored

### openclaw.json Wiring (earlier this week)
- Fixed Chad→Cerebronn gap: added `instructions` block so Chad's session config points to Cerebronn inbox

### Quanta Agent (earlier this week)
- Running on `quanta-v3/safety-fallback` branch in `mission-control-workspace`
- Monitors CallistoFX signals → executes OANDA trades
- Service crashes on startup; runs from terminal as workaround
- Branch is 1 commit ahead of origin — needs push

### Helios (established, running since ~Feb 22)
- Continuous monitoring, 50+ audit reports generated daily
- Sends morning/evening digests to Chad inbox
- Silence alert threshold: ~20 min for active agents

---

## Patterns That Work

### Writing to Agent Inboxes
Every agent communicates via file-based messaging. Pattern:
```python
import json, time
from pathlib import Path

msg = {"type": "task", "from": "chad-yi", "timestamp": time.time(), "content": {...}}
path = Path("/home/chad-yi/.openclaw/workspace/agents/{agent}/inbox/{filename}.json")
path.write_text(json.dumps(msg, indent=2))
```

### How Cerebronn's Inbox Works
- Drop `.md` or `.json` files into `/home/chad-yi/.openclaw/workspace/agents/cerebronn/inbox/`
- Cerebronn picks them up on his next 30-min cycle
- Session reports → `.md` files named `chad-session-{TIMESTAMP}.md`
- Task requests → `.json` files named `task-{TIMESTAMP}.json`

### Forger Brief Format
Drop in `/home/chad-yi/.openclaw/workspace/agents/forger/inbox/` as a `.md` file:
```markdown
# TASK — [Company Name] Website Build

**Company:** [Name]
**Domain:** [domain.com]
**Colors:** [primary #hex] + [accent #hex]
**Font:** [Google Font name]
**Pages:** Home, About, Services, Contact
**Tone:** [Professional/Energetic/etc]

## Copy
[Key headlines, taglines, service descriptions]

## Special Requirements
[Mobile-first, GSAP animations, contact form, etc]
```

### Checking Agent Health Quickly
```bash
# All services at once
systemctl --user status cerebronn.service helios.service forger.service --no-pager | grep -E "Active:|●"

# Recent logs
journalctl --user -u forger.service -n 10 --no-pager
```

---

## Mistakes to Avoid

1. **Acting without reading briefing.md first.** It causes duplicate work and contradicts decisions already made.

2. **Writing to `DATA/data.json` off-path.** It lives in `mission-control-workspace/DATA/data.json`. Double-check the path.

3. **Confusing the two git repos.** Agent infra work → commit to `.openclaw/workspace`. Trading/dashboard → commit to `mission-control-workspace`.

4. **Assuming dormant agents are broken.** Escritor, Autour, MensaMusa are INTENTIONALLY dormant. Helios silence alerts for them are noise — ignore or suppress.

5. **Forgetting to close the loop with Cerebronn.** Session ends without a report = Cerebronn gets no signal. Next session starts even more blind.

6. **Using system python instead of venv.** Always activate venv first.

7. **Touching Cerebronn's memory directory directly.** Only Cerebronn writes there. To update Caleb profile or long-term state, write to Cerebronn's inbox with instructions.

---

## Keys & Auth (Don't Store Here — Know Where They Are)

- **OANDA API key:** in `mission-control-workspace/agents/quanta-v3/` config files
- **Telegram auth:** `mission-control-workspace/quanta_temp_reader.session` (Telethon session)
- **OpenClaw token:** OpenClaw handles auth — never hardcode

---

## Git History (Key Commits)

| Hash | What It Did |
|------|------------|
| `8efd3f2a` | Forger full identity stack (SOUL, SKILL, LEARNING, current-task) |
| `775bfca8` | Forger agent launch — 66 files, service, heartbeat, templates |
| `6ca693ff` | Cerebronn dormant learning loop fix |
| `35554dcb` | ACTIVE.md status keyword requirements added to LEARNING.md |
| `d6661c38` | Quanta trade monitoring |
| `1aca1cb6` | Chad heartbeat schedule updated (cron, 2-hour intervals) |
| `5b7b98df` | Cleanup: nudge spam removed, helios digests added, gitignore |

---

*This file is Chad's memory substitute. Update it at the end of sessions where something important was learned, built, or decided.*
