# LEARNING.md — Cerebronn

*Accumulated intelligence — what this system has learned to do better. Update after every meaningful cycle or decision.*

---

## Architecture Clarifications

### How Cerebronn actually works (two-part system)
- **`cerebronn.py` (systemd service)** — the automated metabolism. Pure Python, zero LLM cost. Runs every 30 minutes. Reads inbox, updates state, applies decision tiers, rewrites briefing.md. This is what keeps memory alive between sessions.
- **Cerebronn in OpenClaw (you)** — the higher brain. Called when Caleb/Chad needs strategic thinking, not just pattern matching. You apply judgment the script cannot.

### The memory split: workspace vs AGENT_HOME
- **OpenClaw reads workspace:** `/home/chad-yi/.openclaw/workspace/agents/cerebronn/` — this is where SOUL.md, SKILL.md, LEARNING.md, current-task.md live (what you're reading now).
- **Background script reads AGENT_HOME:** `/home/chad-yi/.openclaw/agents/cerebronn/memory/` — state.json, briefing.md, archives. This is also what you should read via `memory/` prefix.
- **Important:** These are two different paths. The workspace is what OpenClaw shows you. The memory/ folder is the persistent brain.

---

## Decision Engine Patterns

### Tier 3 noise — Dormant agents
- `escritor`, `mensamusa`, `autour` are intentionally dormant (not running). 
- They generate false Tier 3 alerts about silence.
- **Fix:** These should be in the `DORMANT_AGENTS` set in `cerebronn.py`. Check `AGENT_SERVICES` dict and exclude dormant ones from silence alerts.
- As of Mar 2, 2026: escritor has 370h silence alerts accumulating. These are noise. Resolve by marking escritor dormant.

### Task count always shows 0 in briefing
- The `state.tasks` shows all zeros but Helios reports 17 tasks with 4 critical.
- Root cause: Helios's JSON reports don't include `active_md.summary` in the format Cerebronn expects, or ACTIVE.md path differs between Helios and Cerebronn.
- **Workaround:** Read tasks directly from Helios log or ask Helios to check ACTIVE.md.
- **To fix:** Verify what `active_md` key Helios actually writes in its `helios-report-*.json` files.

---

## Communication Patterns

### How Chad sends session reports to Cerebronn
- Chad should drop a `chad-session-{ts}.md` file into `agents/cerebronn/inbox/`
- The background script picks it up → appends to `memory/decisions/chad-sessions.md`
- As of Mar 2, 2026: Chad has NOT been doing this because his identity wasn't loading properly. Now fixed.

### How Helios talks to Cerebronn
- `helios-report-{ts}.json` every 15min (full audit) and 1 hour (full report)
- `daily-digest-{ts}.md` morning and evening
- All processed by cerebronn.py background script → archived after processing

### How Cerebronn talks to Chad
- Drop `.md` files into `agents/chad-yi/inbox/`
- Chad reads inbox at session start (as of Mar 2, 2026: 35 messages accumulated)
- Naming: `cerebronn-medium-{ts}.md` for Tier 2, `cerebronn-urgent-{ts}.md` for Tier 3

---

## Known Issues (as of Mar 2, 2026)

| Issue | Status | Resolution |
|-------|--------|-----------|
| Task count shows 0 in briefing | Active | Need to trace Helios JSON → active_md path |
| Escritor/mensamusa/autour Tier 3 noise | Active | Mark as dormant in cerebronn.py |
| Cerebronn shows as UNKNOWN in its own briefing | Active | Self-heartbeat not implemented |
| Chad inbox has 35 unread messages | Active | Chad now has identity loaded, will start reading |
| URGENT-verify-helios from Feb 28 | Stale | Should be cleared/archived |

---

## Memory Management Rules

1. `briefing.md` — max 80 lines. Auto-rewritten every cycle. Never append, only rewrite.
2. `state.json` — max 50 agents. Compact. Never grows.
3. Decision logs — monthly files. Auto-compressed to `patterns.md` at month end.
4. Archives — 90-day retention. Auto-purged by cerebronn.py.

---

## Strategic Priorities Learned

1. **Chad's session continuity is the #1 infrastructure problem.** Until Chad auto-loads his identity and briefing, everything else is a secondary problem. (Fixed Mar 2, 2026.)
2. **Forger has 4 pending builds.** The business can't grow without websites. Forger needs to be invocable as an OpenClaw agent so Chad can actually commission builds.
3. **Helios → Cerebronn → Chad pipeline is healthy.** The data flows. The gap is Chad not actioning it. Now fixed with Telegram delivery.
