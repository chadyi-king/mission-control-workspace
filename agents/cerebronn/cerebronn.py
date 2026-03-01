#!/usr/bin/env python3
"""
cerebronn.py — Cerebronn Heartbeat Script
The Persistent Memory & Strategic Brain. Runs every 30 minutes.

What this script does (NO LLM - pure Python):
  - Reads Helios reports from inbox → extracts structured data
  - Updates memory/state.json  → compact rolling state (anti-bloat)
  - Rewrites memory/briefing.md → clean every cycle, never grows
  - Runs tiered decision engine:
      Tier 1 (Simple)  → auto-resolve, log it
      Tier 2 (Medium)  → write to chad-yi inbox, wait for approval
      Tier 3 (Human)   → urgent file to chad-yi inbox + helios inbox
  - Archives processed reports to memory/archive/YYYY-MM/
  - Keeps memory compact: briefing ≤ 80 lines, state.json ≤ 50 agents

The LLM thinking (Kimi K2.5) happens when YOU open Cerebronn
in VS Code / OpenClaw — not in this background loop. This keeps
token costs at ZERO for routine memory management.

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
import time
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

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

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
log = logging.getLogger("cerebronn")

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
        return {
            "ts": data.get("timestamp") or data.get("ts") or str(path.stem.split("-")[-1]),
            "agents": data.get("agents", {}),
            "tasks": data.get("tasks") or data.get("active_md", {}).get("summary", {}),
            "active_md": data.get("active_md", {}),
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

    # Update task summary
    tasks = report.get("tasks", {})
    active_md = report.get("active_md", {})
    summary = active_md.get("summary", {}) if isinstance(active_md, dict) else {}
    if summary:
        state["tasks"] = {
            "total": summary.get("total", state["tasks"]["total"]),
            "active": summary.get("in_progress", state["tasks"]["active"]),
            "blocked": summary.get("blocked", state["tasks"]["blocked"]),
            "critical": summary.get("critical", state["tasks"]["critical"]),
            "urgent": summary.get("urgent", state["tasks"]["urgent"]),
            "completed_today": state["tasks"].get("completed_today", 0)
        }
    elif isinstance(tasks, dict):
        for k in ["total", "active", "blocked", "critical", "urgent"]:
            if k in tasks:
                state["tasks"][k] = tasks[k]

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
    pending2 = state.get("pending_tier2", [])
    pending3 = state.get("pending_tier3", [])

    # Agent status table
    agent_rows = []
    for name, info in sorted(agents.items()):
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

    content = f"""# BRIEFING — For Chad (Session Start)
*Auto-updated by Cerebronn. Last: {sgt_str()} | Cycle #{state.get('cycle_count', 0)}*

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

---

## Pending Decisions — Tier 2 (Inform Chad)
{chr(10).join(pending2_lines) if pending2_lines else '- None'}

## Pending Decisions — Tier 3 (Needs Caleb)
{chr(10).join(pending3_lines) if pending3_lines else '- None'}

---

## How to Use This Briefing
1. READ THIS FIRST every session.
2. Address any Tier 3 items immediately.
3. Review Tier 2 items and respond by dropping a .md file in cerebronn/inbox/.
4. Check agent statuses before delegating any tasks.

*Edit tasks in: /home/chad-yi/.openclaw/workspace/mission-control-workspace/ACTIVE.md*
*Helios reads ACTIVE.md every 15 min → dashboard auto-deploys.*
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
# Main processing cycle
# ---------------------------------------------------------------------------

def run_cycle():
    log.info(f"[cycle] Starting cycle — {sgt_str()}")

    # Load or initialise state
    state = load_state()
    all_decisions = []
    processed = 0

    # Ensure dirs exist
    INBOX.mkdir(parents=True, exist_ok=True)
    OUTBOX.mkdir(parents=True, exist_ok=True)
    CHAD_INBOX.mkdir(parents=True, exist_ok=True)

    # Collect inbox files sorted oldest→newest
    inbox_files = sorted(INBOX.iterdir()) if INBOX.exists() else []
    report_files = [f for f in inbox_files if f.suffix == ".json" and f.name.startswith("helios-report")]
    digest_files = [f for f in inbox_files if f.name.startswith("digest-") or f.name.startswith("daily-digest")]
    task_files  = [f for f in inbox_files if f.name.startswith("TASK-") or f.name.startswith("task-")]
    other_files = [f for f in inbox_files if f not in report_files + digest_files + task_files]

    log.info(f"[inbox] Found: {len(report_files)} reports, {len(digest_files)} digests, {len(task_files)} tasks, {len(other_files)} other")

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

    # Other files — log and archive
    for f in other_files:
        log.info(f"[inbox] Unrecognised file archived: {f.name}")
        archive_file(f)
        processed += 1

    # Apply decisions
    apply_decisions(all_decisions, state)

    # Log decisions to monthly file
    log_decisions_to_file(all_decisions)

    # Rewrite briefing.md
    rewrite_briefing(state)

    # Update INDEX.md timestamp
    update_index_timestamp()

    # Purge old archives
    purge_old_archives()

    # Save state
    save_json(STATE_FILE, state)

    log.info(
        f"[cycle] Done — {processed} files processed, "
        f"{len(all_decisions)} decisions, "
        f"state saved, briefing updated"
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
