#!/usr/bin/env python3
"""
cerebronn.py — Cerebronn Heartbeat Script
The Persistent Memory & Strategic Brain. Runs every 30 minutes.

What this script does (Ollama LLM for planning, pure Python for watchdog):
  - Reads Helios reports from inbox → extracts structured data
  - Updates memory/state.json  → compact rolling state (anti-bloat)
  - Rewrites memory/briefing.md → clean every cycle, never grows
  - Runs tiered decision engine:
      Tier 1 (Simple)  → auto-resolve, log it
      Tier 2 (Medium)  → write to chad-yi inbox, wait for approval
      Tier 3 (Human)   → urgent file to chad-yi inbox + helios inbox
  - Archives processed reports to memory/archive/YYYY-MM/
  - Keeps memory compact: briefing ≤ 80 lines, state.json ≤ 50 agents

The background loop now calls local Ollama (qwen3) for planning when tasks arrive
or block. Context = caleb-profile + agent registry + patterns. Plans are routed
to Chad inbox (summary) and the relevant agent inbox (full plan).

Additional LLM thinking via OpenClaw happens when YOU open Cerebronn in VS Code.

INBOX  (Helios drops here):
  /home/chad-yi/.openclaw/workspace/agents/cerebronn/inbox/

MEMORY (persistent brain):
  /home/chad-yi/.openclaw/agents/cerebronn/memory/

OUTBOX (Cerebronn writes strategic notes):
  /home/chad-yi/.openclaw/workspace/agents/cerebronn/outbox/
"""

import json
import os
import shutil
import subprocess
import time
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import requests as _requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
WORKSPACE       = Path("/home/chad-yi/.openclaw/workspace")
AGENT_HOME      = Path("/home/chad-yi/.openclaw/agents/cerebronn")
MEMORY          = AGENT_HOME / "memory"
INBOX           = WORKSPACE / "agents" / "cerebronn" / "inbox"
OUTBOX          = WORKSPACE / "agents" / "cerebronn" / "outbox"
CHAD_INBOX      = WORKSPACE / "agents" / "chad-yi" / "inbox"
HELIOS_INBOX    = WORKSPACE / "agents" / "helios" / "inbox"
ARCHIVE_BASE    = MEMORY / "archive"
STATE_FILE      = MEMORY / "state.json"
BRIEFING_FILE   = MEMORY / "briefing.md"
INDEX_FILE      = MEMORY / "INDEX.md"
PATTERNS_FILE   = MEMORY / "decisions" / "patterns.md"

SLEEP_INTERVAL  = 30 * 60   # 30 minutes
MAX_ARCHIVE_AGE_DAYS = 90    # purge archives older than 90 days

# Ollama — local LLM for architectural thinking (no token cost)
OLLAMA_URL   = "http://localhost:11434/api/generate"
THINK_MODEL  = "qwen3:latest"   # best reasoning model available
FORGER_INBOX = WORKSPACE / "agents" / "forger" / "inbox"

# How long before Cerebronn re-thinks the same task (avoid spam)
THINK_COOLDOWN_CYCLES = 4   # ~2 hours at 30min intervals

# Agent heartbeat.json paths — Cerebronn reads these directly every cycle
AGENT_HEARTBEATS = {
    "quanta": Path("/home/chad-yi/mission-control-workspace/agents/quanta-v3/heartbeat.json"),
    "forger": Path("/home/chad-yi/.openclaw/workspace/agents/forger/heartbeat.json"),
}

# Systemd service names — used to auto-detect dormant agents
AGENT_SERVICES = {
    "escritor":  "escritor.service",
    "mensamusa": "mensamusa.service",
    "autour":    "autour.service",
    # quanta excluded — runs via nohup, monitored via AGENT_HEARTBEATS["quanta"]
    "forger":    "forger.service",
    "helios":    "helios.service",
    "cerebronn": "cerebronn.service",
}

# Agents that are intentionally inactive — never alert on these regardless of silence
PERMANENT_DORMANT = {"escritor", "mensamusa", "autour"}

# Runtime dormant set — starts with permanent dormant, expanded each cycle by systemctl auto-detection
DORMANT_AGENTS: set = set(PERMANENT_DORMANT)

SEARCH_INDEX    = MEMORY / "search-index.json"
CALEB_PROFILE   = MEMORY / "caleb-profile.md"
COMPANY_VISION  = MEMORY / "company-vision.md"
CHAD_SESSIONS_LOG = MEMORY / "decisions" / "chad-sessions.md"

# Words to skip when building search index
STOP_WORDS = {
    "the","a","an","and","or","but","in","on","at","to","for","of","is","it",
    "by","as","be","if","no","so","do","we","he","she","my","you","are","was",
    "has","had","not","all","from","this","with","that","have","will","can",
    "its","our","they","their","been","into","than","also","when","then","only"
}

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
log = logging.getLogger("cerebronn")

# ---------------------------------------------------------------------------
# Auto dormant detection + heartbeat readers
# ---------------------------------------------------------------------------

def refresh_dormant_agents() -> set:
    """Check systemctl for each known agent. Return set of inactive agent names.
    Always includes PERMANENT_DORMANT regardless of systemctl result."""
    dormant = set(PERMANENT_DORMANT)
    for agent, service in AGENT_SERVICES.items():
        if agent in ("helios", "cerebronn"):  # these drive themselves
            continue
        try:
            result = subprocess.run(
                ["systemctl", "--user", "is-active", service],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode != 0:  # inactive / failed / not-found
                dormant.add(agent)
        except Exception:
            pass  # if systemctl fails, don't false-positive
    log.info(f"[dormant] Auto-detected dormant agents: {dormant or 'none'}")
    return dormant


def read_agent_heartbeats(state: dict):
    """Read heartbeat.json files from agents that don't report via Helios."""
    for agent_name, path in AGENT_HEARTBEATS.items():
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text())
            ts_str   = data.get("timestamp", "")
            status   = data.get("status", "unknown")
            task     = data.get("currentTask", "")
            blocker  = data.get("blockers")
            silence_h = 0.0
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    diff = sgt_now() - ts.astimezone(timezone(timedelta(hours=8)))
                    silence_h = max(0.0, diff.total_seconds() / 3600)
                except Exception:
                    pass
            state["agents"][agent_name] = {
                "last_seen":     ts_str[:16] if ts_str else "—",
                "status":        status,
                "silence_hours": round(silence_h, 1),
                "notes":         task or "",
                "blockers":      blocker,
            }
            log.info(f"[heartbeat] {agent_name}: {status} | task: {str(task)[:60]}")
        except Exception as e:
            log.warning(f"[heartbeat] Failed reading {agent_name}: {e}")


def process_chad_session_report(f) -> str:
    """Extract summary from a chad-session-*.md file and append to sessions log."""
    try:
        content = f.read_text()
        # Append to persistent sessions log
        CHAD_SESSIONS_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(CHAD_SESSIONS_LOG, "a") as fh:
            fh.write(f"\n---\n*Received: {sgt_str()}*\n\n")
            fh.write(content[:2000])  # cap at 2000 chars per session
            fh.write("\n")
        log.info(f"[chad-session] Logged to sessions log: {f.name}")
        return content
    except Exception as e:
        log.warning(f"[chad-session] Failed reading {f.name}: {e}")
        return ""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sgt_now() -> datetime:
    return datetime.now(timezone(timedelta(hours=8)))

def sgt_str(dt: datetime = None) -> str:
    dt = dt or sgt_now()
    return dt.strftime("%Y-%m-%d %H:%M SGT")

def ms() -> int:
    return int(time.time() * 1000)

def load_json(path: Path, default=None):
    try:
        return json.loads(path.read_text())
    except Exception:
        return default if default is not None else {}

def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str))

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)

def archive_month() -> str:
    return sgt_now().strftime("%Y-%m")

def decision_log_path() -> Path:
    month = sgt_now().strftime("%Y-%m")
    return MEMORY / "decisions" / f"{month}.md"

# ---------------------------------------------------------------------------
# State management — compact, never grows
# ---------------------------------------------------------------------------

def load_state() -> dict:
    default = {
        "last_updated": None,
        "cycle_count": 0,
        "agents": {},           # agent_name → {last_seen, status, silence_hours, notes}
        "tasks": {              # summary counters only
            "total": 0,
            "active": 0,
            "blocked": 0,
            "completed_today": 0,
            "critical": 0,
            "urgent": 0
        },
        "projects": {},         # project_id → {name, status, last_milestone}
        "pending_tier2": [],    # decisions waiting for Chad's approval
        "pending_tier3": [],    # urgent decisions waiting for Caleb
        "last_report_ts": None, # timestamp of last processed Helios report
        "patterns": []          # recurring patterns detected
    }
    state = load_json(STATE_FILE, default)
    # Ensure all keys exist (forward compat)
    for k, v in default.items():
        if k not in state:
            state[k] = v
    return state

# ---------------------------------------------------------------------------
# Parse Helios report
# ---------------------------------------------------------------------------

def parse_helios_report(path: Path) -> dict | None:
    """Extract structured data from a Helios JSON report.
    Returns None if the file can't be parsed."""
    try:
        data = load_json(path)
        if not data:
            return None
        tasks_block = data.get("tasks_from_active_md", {})
        return {
            "ts": data.get("generated_at") or data.get("timestamp") or data.get("ts") or str(path.stem.split("-")[-1]),
            "agents": data.get("agents", {}),
            "tasks": tasks_block.get("summary", {}),
            "active_md": tasks_block,
            "tasks_detail": tasks_block.get("tasks", {}),
            "alerts": data.get("alerts", []),
            "dashboard_pushed": data.get("dashboard_pushed", False),
            "raw_path": str(path),
        }
    except Exception as e:
        log.warning(f"[parse] Failed to parse {path.name}: {e}")
        return None


def parse_digest(path: Path) -> dict | None:
    """Extract key information from a digest .md file."""
    try:
        text = path.read_text()
        return {
            "ts": str(path.stem.split("-")[-1]),
            "type": "digest",
            "content_summary": text[:500],  # keep first 500 chars
            "raw_path": str(path),
        }
    except Exception as e:
        log.warning(f"[parse] Failed to parse digest {path.name}: {e}")
        return None

# ---------------------------------------------------------------------------
# Decision Engine — pure Python rules, zero tokens
# ---------------------------------------------------------------------------

TIER1_LABEL = "AUTO"
TIER2_LABEL = "INFORM_CHAD"
TIER3_LABEL = "NEEDS_CALEB"

def make_decision(desc: str, tier: str, action: str = "", agent: str = "") -> dict:
    return {
        "ts": sgt_str(),
        "tier": tier,
        "desc": desc,
        "agent": agent,
        "action": action,
        "resolved": tier == TIER1_LABEL
    }


def run_decision_engine(state: dict, report: dict) -> list:
    """Evaluate current state and return list of decisions."""
    decisions = []
    agents = report.get("agents", {})
    alerts = report.get("alerts", [])

    for agent_name, agent_data in agents.items():
        # Skip intentionally dormant agents
        if agent_name.lower() in DORMANT_AGENTS:
            continue

        silence_h = 0
        if isinstance(agent_data, dict):
            # Try to get silence from the report structure
            silence_s = agent_data.get("silence_seconds", 0)
            silence_h = silence_s / 3600 if silence_s else 0
            last_seen = agent_data.get("last_file_time") or agent_data.get("last_seen")

        # Tier 1: agent silent <2h → auto log
        if 0.5 < silence_h <= 2:
            d = make_decision(
                f"{agent_name} has been silent for {silence_h:.1f}h — within normal range",
                TIER1_LABEL,
                action="Noted in memory. No action needed.",
                agent=agent_name
            )
            decisions.append(d)

        # Tier 2: agent silent 2-8h → inform Chad
        elif 2 < silence_h <= 8:
            d = make_decision(
                f"{agent_name} silent for {silence_h:.1f}h — may need a nudge",
                TIER2_LABEL,
                action="Drop a nudge file in their inbox and inform Chad.",
                agent=agent_name
            )
            decisions.append(d)

        # Tier 3: agent silent >8h → escalate to Caleb
        elif silence_h > 8:
            d = make_decision(
                f"URGENT: {agent_name} silent for {silence_h:.1f}h — possible failure",
                TIER3_LABEL,
                action="Immediate escalation to Chad → Caleb required.",
                agent=agent_name
            )
            decisions.append(d)

    # Task-level decisions
    task_summary = report.get("tasks", {})
    if isinstance(task_summary, dict):
        blocked = task_summary.get("blocked", 0)
        critical = task_summary.get("critical", 0)

        if critical > 0:
            decisions.append(make_decision(
                f"{critical} CRITICAL task(s) detected in ACTIVE.md",
                TIER3_LABEL,
                action="Caleb must be informed immediately via Chad."
            ))
        elif blocked > 3:
            decisions.append(make_decision(
                f"{blocked} tasks currently blocked — above threshold of 3",
                TIER2_LABEL,
                action="Chad should review blockers and unblock or escalate."
            ))

    # Alert forwarding
    for alert in alerts:
        if "critical" in str(alert).lower() or "corruption" in str(alert).lower():
            decisions.append(make_decision(
                f"Helios alert: {str(alert)[:120]}",
                TIER3_LABEL,
                action="Immediate review required."
            ))

    return decisions


# ---------------------------------------------------------------------------
# Apply decisions
# ---------------------------------------------------------------------------

def apply_decisions(decisions: list, state: dict):
    """Execute Tier 1 silently, write Tier 2/3 to appropriate inboxes."""
    tier2 = [d for d in decisions if d["tier"] == TIER2_LABEL]
    tier3 = [d for d in decisions if d["tier"] == TIER3_LABEL]

    if tier2:
        _write_chad_message("MEDIUM DECISIONS — Your Review Needed", tier2, priority="medium")
        state["pending_tier2"].extend(tier2)
        # Keep pending list compact (last 20 only)
        state["pending_tier2"] = state["pending_tier2"][-20:]
        log.info(f"[decisions] {len(tier2)} Tier 2 decision(s) written to Chad inbox")

    if tier3:
        _write_chad_message("URGENT — Needs Caleb", tier3, priority="urgent")
        _write_helios_alert(tier3)
        state["pending_tier3"].extend(tier3)
        state["pending_tier3"] = state["pending_tier3"][-20:]
        log.info(f"[decisions] {len(tier3)} Tier 3 URGENT decision(s) escalated")

    tier1_count = len([d for d in decisions if d["tier"] == TIER1_LABEL])
    if tier1_count:
        log.info(f"[decisions] {tier1_count} Tier 1 auto-decision(s) logged silently")


def _write_chad_message(subject: str, decisions: list, priority: str = "medium"):
    ts = ms()
    lines = [
        f"# Cerebronn → Chad: {subject}",
        f"*{sgt_str()} | Priority: {priority.upper()}*",
        "",
        "## Decisions Requiring Your Attention",
        ""
    ]
    for i, d in enumerate(decisions, 1):
        lines += [
            f"### {i}. [{d['tier']}] {d['desc']}",
            f"- **Agent:** {d.get('agent') or 'System'}",
            f"- **Recommended action:** {d['action']}",
            f"- **Time:** {d['ts']}",
            ""
        ]
    lines += [
        "---",
        "*Reply by dropping a .md file in cerebronn/inbox/ with your decision.*"
    ]
    write_file(
        CHAD_INBOX / f"cerebronn-{priority}-{ts}.md",
        "\n".join(lines)
    )


def _write_helios_alert(decisions: list):
    ts = ms()
    lines = [
        "# CEREBRONN URGENT ESCALATION",
        f"*{sgt_str()}*",
        "",
        "Cerebronn has identified issues requiring immediate Caleb notification.",
        ""
    ]
    for d in decisions:
        lines += [f"- **{d['desc']}** → {d['action']}", ""]
    lines += ["Please deliver via Telegram to Caleb."]
    write_file(
        HELIOS_INBOX / f"cerebronn-urgent-{ts}.md",
        "\n".join(lines)
    )

# ---------------------------------------------------------------------------
# Update state from report
# ---------------------------------------------------------------------------

def update_state_from_report(state: dict, report: dict):
    """Merge new report data into rolling state. State stays compact."""
    agents_data = report.get("agents", {})
    for agent_name, agent_info in agents_data.items():
        if not isinstance(agent_info, dict):
            continue
        existing = state["agents"].get(agent_name, {})
        silence_s = agent_info.get("silence_seconds", 0)
        state["agents"][agent_name] = {
            "last_seen": agent_info.get("last_file_time") or existing.get("last_seen"),
            "status": agent_info.get("status", existing.get("status", "unknown")),
            "silence_hours": round(silence_s / 3600, 1) if silence_s else 0,
            "last_updated": sgt_str()
        }

    # Update task summary — uses tasks_from_active_md.summary (populated by parse_helios_report)
    tasks = report.get("tasks", {})
    if isinstance(tasks, dict) and (tasks.get("critical") or tasks.get("active") or tasks.get("blocked")):
        computed_total = sum([
            tasks.get("critical", 0),
            tasks.get("urgent", 0),
            tasks.get("active", 0),
            tasks.get("blocked", 0),
            tasks.get("done", 0),
        ])
        state["tasks"] = {
            "total": computed_total,
            "active": tasks.get("active", state["tasks"].get("active", 0)),
            "blocked": tasks.get("blocked", state["tasks"].get("blocked", 0)),
            "critical": tasks.get("critical", state["tasks"].get("critical", 0)),
            "urgent": tasks.get("urgent", state["tasks"].get("urgent", 0)),
            "completed_today": tasks.get("done", state["tasks"].get("completed_today", 0))
        }
        # Persist task detail for briefing (task names)
        if report.get("tasks_detail"):
            state["tasks_detail"] = report["tasks_detail"]

    state["last_report_ts"] = report.get("ts")
    state["last_updated"] = sgt_str()
    state["cycle_count"] = state.get("cycle_count", 0) + 1


# ---------------------------------------------------------------------------
# Rewrite briefing.md — clean every cycle, never grows
# ---------------------------------------------------------------------------

def rewrite_briefing(state: dict):
    """Rewrite briefing.md from current state. Always ≤80 lines."""
    agents = state.get("agents", {})
    tasks = state.get("tasks", {})
    tasks_detail = state.get("tasks_detail", {})
    pending2 = state.get("pending_tier2", [])
    pending3 = state.get("pending_tier3", [])

    # Agent status table (skip intentionally dormant agents)
    agent_rows = []
    for name, info in sorted(agents.items()):
        if name.lower() in DORMANT_AGENTS:
            continue
        status = info.get("status", "unknown").upper()
        last_seen = info.get("last_seen") or "—"
        silence = info.get("silence_hours", 0)
        silence_str = f"{silence}h" if silence else "active"
        agent_rows.append(f"| {name:<15} | {last_seen} | {status:<10} | {silence_str} |")

    # Pending decisions
    pending2_lines = []
    for d in pending2[-5:]:  # only last 5
        pending2_lines.append(f"- [{d['ts']}] {d['desc']}")

    pending3_lines = []
    for d in pending3[-5:]:
        pending3_lines.append(f"- 🚨 [{d['ts']}] {d['desc']}")

    # Scan chad-yi inbox for unread messages
    inbox_urgent = []
    inbox_medium = []
    inbox_digest = []
    inbox_other = []
    if CHAD_INBOX.exists():
        for f in sorted(CHAD_INBOX.iterdir()):
            if not f.suffix == ".md":
                continue
            name = f.name
            if "urgent" in name.lower():
                inbox_urgent.append(name)
            elif "medium" in name.lower() or "inform" in name.lower():
                inbox_medium.append(name)
            elif "digest" in name.lower():
                inbox_digest.append(name)
            else:
                inbox_other.append(name)

    inbox_lines = []
    for fn in inbox_urgent[-3:]:
        inbox_lines.append(f"- 🚨 URGENT: {fn}")
    for fn in inbox_medium[-3:]:
        inbox_lines.append(f"- ⚠️  MEDIUM: {fn}")
    if inbox_digest:
        inbox_lines.append(f"- 📋 {len(inbox_digest)} daily digest(s) waiting")
    for fn in inbox_other[-3:]:
        inbox_lines.append(f"- 📄 {fn}")
    if not inbox_lines:
        inbox_lines = ["- Inbox clear ✓"]

    inbox_total = len(inbox_urgent) + len(inbox_medium) + len(inbox_digest) + len(inbox_other)
    inbox_header = f"## 📬 Chad-Yi Inbox ({inbox_total} messages)"

    # Build critical/urgent task name list from tasks_detail
    critical_task_lines = []
    if tasks_detail:
        priority_order = ["critical", "urgent"]
        for priority in priority_order:
            for tid, tinfo in sorted(tasks_detail.items()):
                if isinstance(tinfo, dict) and tinfo.get("priority") == priority:
                    status = tinfo.get("status", "?")
                    title = tinfo.get("title", tid)
                    icon = "🚨" if priority == "critical" else "⚠️ "
                    critical_task_lines.append(f"- {icon} [{tid}] {title} `{status}`")
    if not critical_task_lines:
        critical_task_lines = ["- (task detail not yet loaded — next cycle will populate)"]

    content = f"""# BRIEFING — For Chad (Session Start)
*Auto-updated by Cerebronn. Last: {sgt_str()} | Cycle #{state.get('cycle_count', 0)}*

---

{inbox_header}
{chr(10).join(inbox_lines)}

*Path: /home/chad-yi/.openclaw/workspace/agents/chad-yi/inbox/*

---

## Agent Status
| Agent           | Last Seen         | Status     | Silence |
|-----------------|-------------------|------------|---------|
{chr(10).join(agent_rows) if agent_rows else '| (no data yet) | — | — | — |'}

---

## Task Summary (from ACTIVE.md)
| Metric     | Count |
|------------|-------|
| Total      | {tasks.get('total', 0)} |
| Active     | {tasks.get('active', 0)} |
| Blocked    | {tasks.get('blocked', 0)} |
| Critical   | {tasks.get('critical', 0)} |
| Urgent     | {tasks.get('urgent', 0)} |

### Critical & Urgent Tasks
{chr(10).join(critical_task_lines)}

---

## Pending Decisions — Tier 2 (Inform Chad)
{chr(10).join(pending2_lines) if pending2_lines else '- None'}

## Pending Decisions — Tier 3 (Needs Caleb)
{chr(10).join(pending3_lines) if pending3_lines else '- None'}

---

## Session Start Checklist
1. Read inbox messages above (urgent first).
2. Address Tier 3 items — these need Caleb.
3. Review agent silences before delegating.
4. Edit tasks: /home/chad-yi/.openclaw/workspace/mission-control-workspace/ACTIVE.md
"""
    write_file(BRIEFING_FILE, content)
    log.info("[briefing] Rewritten")


# ---------------------------------------------------------------------------
# Append to monthly decision log
# ---------------------------------------------------------------------------

def log_decisions_to_file(decisions: list):
    if not decisions:
        return
    log_path = decision_log_path()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    if not log_path.exists():
        lines.append(f"# Decision Log — {sgt_now().strftime('%B %Y')}\n\n")

    for d in decisions:
        tier_icon = {"AUTO": "✅", "INFORM_CHAD": "🟡", "NEEDS_CALEB": "🚨"}.get(d["tier"], "•")
        lines.append(f"## {tier_icon} {d['ts']} | {d['tier']}")
        lines.append(f"**{d['desc']}**")
        if d.get("agent"):
            lines.append(f"- Agent: {d['agent']}")
        lines.append(f"- Action: {d['action']}")
        lines.append("")

    with open(log_path, "a") as f:
        f.write("\n".join(lines))

    log.info(f"[log] {len(decisions)} decision(s) appended to {log_path.name}")


# ---------------------------------------------------------------------------
# Archive processed inbox files — anti-bloat
# ---------------------------------------------------------------------------

def archive_file(path: Path):
    """Move processed file to memory/archive/YYYY-MM/"""
    dest_dir = ARCHIVE_BASE / archive_month()
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / path.name
    try:
        shutil.move(str(path), str(dest))
    except Exception as e:
        log.warning(f"[archive] Could not archive {path.name}: {e}")


def purge_old_archives():
    """Delete archive folders older than MAX_ARCHIVE_AGE_DAYS. Runs once per cycle."""
    if not ARCHIVE_BASE.exists():
        return
    cutoff = sgt_now() - timedelta(days=MAX_ARCHIVE_AGE_DAYS)
    for folder in ARCHIVE_BASE.iterdir():
        if not folder.is_dir():
            continue
        try:
            folder_date = datetime.strptime(folder.name, "%Y-%m").replace(
                tzinfo=timezone(timedelta(hours=8))
            )
            if folder_date < cutoff:
                shutil.rmtree(str(folder))
                log.info(f"[archive] Purged old archive: {folder.name}")
        except ValueError:
            pass  # not a date folder, skip


# ---------------------------------------------------------------------------
# Update INDEX.md timestamp
# ---------------------------------------------------------------------------

def update_index_timestamp():
    """Update the 'last updated' timestamps in the INDEX file."""
    if not INDEX_FILE.exists():
        return
    text = INDEX_FILE.read_text()
    now = sgt_str()
    # Update briefing.md row
    import re
    text = re.sub(
        r'\| briefing\.md\s*\|[^|]+\|[^|]+\|',
        f'| briefing.md | {now} | cerebronn-auto |',
        text
    )
    INDEX_FILE.write_text(text)


# ---------------------------------------------------------------------------
# Search index — keyword → file path map (anti token-bloat)
# ---------------------------------------------------------------------------

def build_search_index():
    """Scan all memory .md files, extract keywords, write search-index.json.
    Cerebronn reads this before opening any file — avoids full scans."""
    index: dict[str, list[str]] = {}
    scan_dirs = [
        MEMORY,
        MEMORY / "agents",
        MEMORY / "decisions",
        MEMORY / "projects",
        MEMORY / "tasks",
    ]

    files_scanned = 0
    for d in scan_dirs:
        if not d.exists():
            continue
        for f in d.iterdir():
            if f.suffix not in (".md", ".json") or f.name.startswith("_"):
                continue
            if f == SEARCH_INDEX:
                continue
            try:
                text = f.read_text(errors="ignore").lower()
                # Extract meaningful words (≥4 chars, alpha-only)
                import re
                words = set(re.findall(r"[a-z]{4,}", text))
                words -= STOP_WORDS
                rel_path = str(f.relative_to(MEMORY))
                for word in words:
                    if word not in index:
                        index[word] = []
                    if rel_path not in index[word]:
                        index[word].append(rel_path)
                files_scanned += 1
            except Exception:
                pass

    # Keep index lean: drop keywords that match all files (too common to be useful)
    max_useful = max(1, files_scanned - 2)
    index = {k: v for k, v in index.items() if len(v) <= max_useful}

    save_json(SEARCH_INDEX, {"built": sgt_str(), "files_indexed": files_scanned, "index": index})
    log.info(f"[search-index] Built — {files_scanned} files, {len(index)} keywords")


# ---------------------------------------------------------------------------
# Ollama Thinking Engine — architecture planning, gap analysis, routing
# ---------------------------------------------------------------------------

def call_ollama(prompt: str, timeout: int = 90) -> str | None:
    """Call local Ollama and return the response text. Returns None on failure."""
    if not HAS_REQUESTS:
        log.warning("[think] requests not installed — cannot call Ollama")
        return None
    try:
        r = _requests.post(
            OLLAMA_URL,
            json={"model": THINK_MODEL, "prompt": prompt, "stream": False},
            timeout=timeout,
        )
        if r.ok:
            return r.json().get("response", "").strip()
        else:
            log.warning(f"[think] Ollama error {r.status_code}: {r.text[:120]}")
            return None
    except Exception as e:
        log.warning(f"[think] Ollama unreachable: {e}")
        return None


def build_think_context(state: dict) -> str:
    """Assemble rich context from memory for the LLM: profile, agents, tasks, patterns."""
    parts = []

    # Caleb's profile
    if CALEB_PROFILE.exists():
        parts.append("=== CALEB PROFILE ===\n" + CALEB_PROFILE.read_text()[:1500])

    # Agent registry
    registry = MEMORY / "agents" / "REGISTRY.md"
    if registry.exists():
        parts.append("=== AGENT REGISTRY ===\n" + registry.read_text()[:1200])

    # Patterns
    if PATTERNS_FILE.exists():
        parts.append("=== KNOWN PATTERNS ===\n" + PATTERNS_FILE.read_text()[:800])

    # Current system state summary
    tasks = state.get("tasks", {})
    agents_summary = ", ".join(
        f"{n}:{i.get('status','?')}" for n, i in state.get("agents", {}).items()
    )
    parts.append(
        f"=== CURRENT STATE ===\n"
        f"Tasks — Total:{tasks.get('total',0)} Critical:{tasks.get('critical',0)} "
        f"Urgent:{tasks.get('urgent',0)} Blocked:{tasks.get('blocked',0)} "
        f"Active:{tasks.get('active',0)}\n"
        f"Agents — {agents_summary}"
    )

    return "\n\n".join(parts)


def think_on_task(task_id: str, task_info: dict, state: dict) -> str | None:
    """Call Ollama to produce an architectural plan for a task. Returns plan text."""
    context = build_think_context(state)
    title   = task_info.get("title", task_id)
    status  = task_info.get("status", "?")
    priority = task_info.get("priority", "?")
    agent   = task_info.get("agent", "unassigned")

    prompt = f"""You are Cerebronn, the strategic brain of an AI agent system called Mission Control.
Your job is to analyse tasks and produce clear, actionable plans for the team.

{context}

=== TASK TO ANALYSE ===
ID: {task_id}
Title: {title}
Priority: {priority}
Status: {status}
Assigned to: {agent}

Produce a structured analysis with these sections:
1. ROOT CAUSE — Why is this task blocked or complex? Be specific.
2. ARCHITECTURE — How should this be properly built/solved? What is the right structure?
3. GAPS — What information, credentials, decisions, or research is missing?
4. RESEARCH SOURCES — Where specifically should we look? (GitHub repos, Twitter accounts,
   YouTube channels, docs, APIs, tools — be specific, not generic)
5. EXECUTION PLAN — Numbered steps in the right order. Which agent does each step?
   (Agents: Chad-Yi=coordinator/Caleb's voice, Helios=monitoring, Forger=website builder,
   Quanta=forex trading bot, Cerebronn=memory/planning)
6. BLOCKERS FOR CALEB — What specifically needs Caleb's decision or action?

Be concise and direct. No fluff. Focus on what will actually unblock progress."""

    log.info(f"[think] Calling Ollama for task {task_id}: {title[:50]}...")
    plan = call_ollama(prompt)
    if plan:
        log.info(f"[think] Plan generated for {task_id} ({len(plan)} chars)")
    return plan


def route_plan(task_id: str, task_info: dict, plan_text: str):
    """Write plan to Chad inbox (summary) and relevant agent inbox (full plan)."""
    now_ts = sgt_str()
    stamp  = str(int(time.time()))
    title  = task_info.get("title", task_id)
    agent  = task_info.get("agent", "").lower()
    priority = task_info.get("priority", "?")

    # --- Chad inbox: always gets a summary (first 600 chars + pointer)
    chad_subject = f"Cerebronn Plan: [{task_id}] {title}"
    plan_snippet = plan_text[:600]
    overflow_note = "\n\n_...full plan sent to relevant agent inbox_" if len(plan_text) > 600 else ""
    chad_content = f"""# {chad_subject}
*Generated: {now_ts} | Priority: {priority}*

{plan_snippet}{overflow_note}

---
*Auto-generated by Cerebronn (qwen3). Review and delegate as needed.*
"""
    chad_file = CHAD_INBOX / f"cerebronn-plan-{task_id.lower()}-{stamp}.md"
    chad_file.parent.mkdir(parents=True, exist_ok=True)
    chad_file.write_text(chad_content)
    log.info(f"[route] Plan summary → Chad inbox: {chad_file.name}")

    # --- Agent inbox: full plan routed by task type / assigned agent
    full_content = f"""# Cerebronn Plan: [{task_id}] {title}
*Generated: {now_ts} | Priority: {priority} | Assigned: {task_info.get('agent','?')}*

{plan_text}

---
*Auto-generated by Cerebronn (qwen3). Act on this plan.*
"""

    targets = []
    if "forger" in agent or any(kw in title.lower() for kw in ["website", "build", "design", "site", "page"]):
        targets.append((FORGER_INBOX, "forger"))
    if "helios" in agent or any(kw in title.lower() for kw in ["monitor", "track", "audit", "report"]):
        targets.append((WORKSPACE / "agents" / "helios" / "inbox", "helios"))
    if not targets:
        # Default: write to cerebronn outbox for reference
        targets.append((OUTBOX, "cerebronn-outbox"))

    for inbox_dir, target_name in targets:
        inbox_dir.mkdir(parents=True, exist_ok=True)
        dest = inbox_dir / f"cerebronn-plan-{task_id.lower()}-{stamp}.md"
        dest.write_text(full_content)
        log.info(f"[route] Full plan → {target_name} inbox: {dest.name}")


def run_think_loop(state: dict, new_task_ids: list):
    """Think on tasks that need planning. Called every cycle.
    Triggers on: new tasks, blocked critical tasks, explicit think-requests.
    Uses cooldown to avoid re-thinking the same task every cycle."""
    if not HAS_REQUESTS:
        return

    think_log = state.setdefault("think_log", {})   # task_id → cycle_count_last_thought
    current_cycle = state.get("cycle_count", 0)
    tasks_detail = state.get("tasks_detail", {})
    candidates = []  # list of (task_id, task_info, reason)

    # 1. New tasks that just arrived
    for tid in new_task_ids:
        info = tasks_detail.get(tid, {"title": tid, "priority": "unknown", "status": "new"})
        candidates.append((tid, info, "new task"))

    # 2. Blocked critical/urgent tasks (with cooldown)
    for tid, tinfo in tasks_detail.items():
        if tinfo.get("status") not in ("blocked", "active"):
            continue
        if tinfo.get("priority") not in ("critical", "urgent"):
            continue
        last_thought = think_log.get(tid, 0)
        if current_cycle - last_thought >= THINK_COOLDOWN_CYCLES:
            if tid not in [c[0] for c in candidates]:  # not already added
                candidates.append((tid, tinfo, f"{tinfo['status']} {tinfo['priority']}"))

    # 3. Explicit think-request files in inbox (already archived by now — check outbox log)
    # (Users can drop think-request-TASKID.md to force a re-think)

    if not candidates:
        return

    log.info(f"[think] {len(candidates)} task(s) queued for thinking")
    for task_id, task_info, reason in candidates:
        plan = think_on_task(task_id, task_info, state)
        if plan:
            route_plan(task_id, task_info, plan)
            think_log[task_id] = current_cycle
            append_caleb_observation(
                f"Cerebronn planned [{task_id}] '{task_info.get('title','')}' — {reason}"
            )


# ---------------------------------------------------------------------------
# Learning loop — append observed patterns to caleb-profile.md
# ---------------------------------------------------------------------------

def append_caleb_observation(observation: str):
    """Add a timestamped observation line to caleb-profile.md Observed Patterns section."""
    if not CALEB_PROFILE.exists():
        return
    marker = "## Observed Patterns"
    try:
        text = CALEB_PROFILE.read_text()
        if marker not in text:
            return
        line = f"- {sgt_str()[:10]}: {observation}"
        # Insert after the marker line
        text = text.replace(marker + "\n", marker + "\n" + line + "\n", 1)
        CALEB_PROFILE.write_text(text)
        log.info(f"[learn] Caleb profile updated: {observation[:60]}")
    except Exception as e:
        log.warning(f"[learn] Could not update caleb-profile: {e}")


def run_learning_loop(state: dict, all_decisions: list):
    """Detect patterns from this cycle's data and update caleb-profile.md."""
    observations = []

    # Pattern: same agent repeatedly silent across cycles
    for agent, info in state.get("agents", {}).items():
        if agent.lower() in DORMANT_AGENTS:
            continue  # skip intentionally stopped agents
        silence_h = info.get("silence_hours", 0)
        if silence_h > 24:
            observations.append(
                f"{agent} has been silent for {silence_h:.0f}h — may be an inactive/unbuilt agent"
            )

    # Pattern: high blocked task count
    blocked = state.get("tasks", {}).get("blocked", 0)
    if blocked >= 3:
        observations.append(
            f"System has {blocked} blocked tasks — Caleb typically unblocks with credential/access decisions"
        )

    # Pattern: recurring Tier 3 decisions (urgent escalations)
    tier3_count = len([d for d in all_decisions if d["tier"] == TIER3_LABEL])
    if tier3_count >= 2:
        observations.append(
            f"{tier3_count} urgent escalations in one cycle — review whether Tier 3 threshold needs adjusting"
        )

    # Write new observations (deduplicate against recent profile content)
    if CALEB_PROFILE.exists():
        existing = CALEB_PROFILE.read_text()
        for obs in observations:
            # Avoid exact duplicates from same day
            short_key = obs[:40]
            if short_key not in existing:
                append_caleb_observation(obs)


# ---------------------------------------------------------------------------
# Monthly compression — distil decisions into patterns.md
# ---------------------------------------------------------------------------

def run_monthly_compression():
    """On the 1st of each month: compress last month's decision log into patterns.md.
    Archives the raw log after extracting lessons. Keeps patterns.md ≤ 60 lines."""
    today = sgt_now()
    if today.day != 1:
        return  # only run on 1st of month

    # Identify last month
    first_of_this_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_dt = first_of_this_month - timedelta(days=1)
    last_month_str = last_month_dt.strftime("%Y-%m")
    log_file = MEMORY / "decisions" / f"{last_month_str}.md"

    if not log_file.exists():
        return

    try:
        text = log_file.read_text()
        lines = text.splitlines()

        # Count decision types from the raw log
        tier_counts = {TIER1_LABEL: 0, TIER2_LABEL: 0, TIER3_LABEL: 0}
        agents_flagged: dict[str, int] = {}
        for line in lines:
            for tier in tier_counts:
                if tier in line:
                    tier_counts[tier] += 1
            # Extract agent names mentioned
            import re
            agent_matches = re.findall(r"Agent: (\w+)", line)
            for a in agent_matches:
                agents_flagged[a] = agents_flagged.get(a, 0) + 1

        total = sum(tier_counts.values())
        top_agents = sorted(agents_flagged.items(), key=lambda x: x[1], reverse=True)[:3]

        # Build compressed pattern entry
        month_label = last_month_dt.strftime("%B %Y")
        pattern_entry = [
            f"\n## {month_label} — Compressed ({total} decisions)",
            f"- Auto (Tier 1): {tier_counts[TIER1_LABEL]} | Inform Chad (Tier 2): {tier_counts[TIER2_LABEL]} | Needs Caleb (Tier 3): {tier_counts[TIER3_LABEL]}",
        ]
        if top_agents:
            agents_str = ", ".join(f"{a}({c}x)" for a, c in top_agents)
            pattern_entry.append(f"- Most flagged agents: {agents_str}")
        if tier_counts[TIER3_LABEL] > 5:
            pattern_entry.append(
                f"- ⚠️ High Tier 3 count ({tier_counts[TIER3_LABEL]}) — review escalation thresholds"
            )
        pattern_entry.append(f"- Raw log archived to memory/archive/{last_month_str}/")
        pattern_entry.append("")

        # Append to patterns.md
        PATTERNS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PATTERNS_FILE, "a") as f:
            f.write("\n".join(pattern_entry))

        # Trim patterns.md to 80 lines max (keep recent)
        if PATTERNS_FILE.exists():
            all_lines = PATTERNS_FILE.read_text().splitlines()
            if len(all_lines) > 80:
                PATTERNS_FILE.write_text("\n".join(all_lines[-80:]))

        # Archive the raw log
        archive_dir = ARCHIVE_BASE / last_month_str
        archive_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(log_file), str(archive_dir / log_file.name))

        log.info(f"[compress] {month_label} compressed into patterns.md — {total} decisions")

    except Exception as e:
        log.warning(f"[compress] Monthly compression failed: {e}")


# ---------------------------------------------------------------------------
# Main processing cycle
# ---------------------------------------------------------------------------

def run_cycle():
    global DORMANT_AGENTS
    log.info(f"[cycle] Starting cycle — {sgt_str()}")

    # Load or initialise state
    state = load_state()
    all_decisions = []
    processed = 0

    # Auto-detect dormant agents (uses systemctl — no LLM)
    DORMANT_AGENTS = refresh_dormant_agents()

    # Ensure dirs exist
    INBOX.mkdir(parents=True, exist_ok=True)
    OUTBOX.mkdir(parents=True, exist_ok=True)
    CHAD_INBOX.mkdir(parents=True, exist_ok=True)

    # Read agent heartbeat files directly (Quanta + others)
    read_agent_heartbeats(state)

    # Collect inbox files sorted oldest→newest
    inbox_files = sorted(INBOX.iterdir()) if INBOX.exists() else []
    report_files   = [f for f in inbox_files if f.suffix == ".json" and f.name.startswith("helios-report")]
    forger_files   = [f for f in inbox_files if f.suffix == ".json" and f.name.startswith("forger-status")]
    digest_files   = [f for f in inbox_files if f.name.startswith("digest-") or f.name.startswith("daily-digest")]
    task_files     = [f for f in inbox_files if f.name.startswith("TASK-") or f.name.startswith("task-")]
    session_files  = [f for f in inbox_files if f.name.startswith("chad-session-")]
    think_req_files = [f for f in inbox_files if f.name.startswith("think-request-")]
    other_files    = [f for f in inbox_files if f not in report_files + forger_files + digest_files + task_files + session_files + think_req_files]

    log.info(f"[inbox] Found: {len(report_files)} reports, {len(forger_files)} forger-status, {len(digest_files)} digests, {len(task_files)} tasks, {len(session_files)} chad-sessions, {len(think_req_files)} think-requests, {len(other_files)} other")

    # Process Helios reports — latest only to avoid repeating old data
    # But archive ALL of them after reading the latest
    if report_files:
        # Parse latest for state update + decisions
        latest = report_files[-1]
        report = parse_helios_report(latest)
        if report:
            update_state_from_report(state, report)
            decisions = run_decision_engine(state, report)
            all_decisions.extend(decisions)
            log.info(f"[reports] Latest report processed: {latest.name} → {len(decisions)} decision(s)")

        # Archive all reports (including latest after processing)
        for f in report_files:
            archive_file(f)
            processed += 1

    # Process Forger status reports — update state with build queue info
    for f in forger_files:
        try:
            data = json.loads(f.read_text())
            builds = data.get("builds", {})
            pending = sum(1 for b in builds.values() if b.get("status") == "pending")
            ready   = sum(1 for b in builds.values() if b.get("status") == "ready_for_review")
            state.setdefault("agents", {})["forger"] = {
                "last_seen": data.get("timestamp", sgt_str()),
                "status": "running",
                "silence_hours": 0,
                "notes": data.get("summary", f"{pending} pending, {ready} ready"),
                "builds_pending": pending,
                "builds_ready": ready,
            }
            log.info(f"[forger] Build queue: {data.get('summary', 'updated')}")
        except Exception as e:
            log.warning(f"[forger] Failed parsing {f.name}: {e}")
        archive_file(f)
        processed += 1

    # Process digests — just archive them (content already sent to Telegram)
    for f in digest_files:
        archive_file(f)
        processed += 1

    # Process task files — log they were received
    for f in task_files:
        try:
            content = f.read_text()[:300]
            log.info(f"[task] Received task file: {f.name}")
            # Tier 2: task files always need Chad's attention
            all_decisions.append(make_decision(
                f"New task instruction received: {f.name}",
                TIER2_LABEL,
                action=f"Review and assign. File content preview: {content[:100]}..."
            ))
        except Exception:
            pass
        archive_file(f)
        processed += 1

    # Chad session reports — log into persistent sessions memory
    for f in session_files:
        session_content = process_chad_session_report(f)
        if session_content:
            all_decisions.append(make_decision(
                f"Chad session report received: {f.name}",
                TIER1_LABEL,
                action="Logged to chad-sessions.md for memory."
            ))
        archive_file(f)
        processed += 1

    # Other files — log and archive
    for f in other_files:
        log.info(f"[inbox] Unrecognised file archived: {f.name}")
        archive_file(f)
        processed += 1

    # Thinking loop — call Ollama to plan tasks that need it
    # new_task_ids: tasks from task_files dropped this cycle (force immediate think)
    new_task_ids = [
        f.stem.replace("TASK-", "").replace("task-", "")
        for f in task_files
    ]
    # Also force re-think on any explicit think-request-TASKID.md files
    for f in think_req_files:
        tid = f.stem.replace("think-request-", "").strip()
        if tid and tid not in new_task_ids:
            new_task_ids.append(tid)
            # Reset cooldown so it gets re-thought immediately
            state.get("think_log", {}).pop(tid, None)
        archive_file(f)
        processed += 1
    run_think_loop(state, new_task_ids)

    # Apply decisions
    apply_decisions(all_decisions, state)

    # Log decisions to monthly file
    log_decisions_to_file(all_decisions)

    # Rewrite briefing.md
    rewrite_briefing(state)

    # Update INDEX.md timestamp
    update_index_timestamp()

    # Rebuild search index (fast keyword scan of all memory files)
    build_search_index()

    # Learning loop — detect patterns, update caleb-profile.md
    run_learning_loop(state, all_decisions)

    # Monthly compression (only runs on 1st of month)
    run_monthly_compression()

    # Purge old archives
    purge_old_archives()

    # Save state
    save_json(STATE_FILE, state)

    log.info(
        f"[cycle] Done — {processed} files processed, "
        f"{len(all_decisions)} decisions, "
        f"state saved, briefing + search-index updated"
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    log.info("=" * 60)
    log.info("Cerebronn — Persistent Memory & Strategic Brain — STARTED")
    log.info(f"Memory home : {AGENT_HOME}")
    log.info(f"Inbox       : {INBOX}")
    log.info(f"Sleep cycle : {SLEEP_INTERVAL // 60} minutes")
    log.info("=" * 60)

    # Ensure base dirs exist
    for d in [MEMORY, INBOX, OUTBOX, CHAD_INBOX, ARCHIVE_BASE,
              MEMORY / "agents", MEMORY / "tasks",
              MEMORY / "decisions", MEMORY / "projects"]:
        d.mkdir(parents=True, exist_ok=True)

    while True:
        try:
            run_cycle()
        except Exception as e:
            log.error(f"[cycle] Unhandled error: {e}", exc_info=True)

        log.info(f"[sleep] Next cycle in {SLEEP_INTERVAL // 60} minutes")
        time.sleep(SLEEP_INTERVAL)


if __name__ == "__main__":
    main()
