#!/usr/bin/env python3
"""
helios-v2.py — Helios Local Agent
Runs as a background process. Mission Control Engineer.

Responsibilities (never stops):
  - Every 15 min : audit all agents (check inbox/outbox activity)
  - Every 15 min : POST heartbeat to Helios API
  - Every 15 min : parse ACTIVE.md -> update data.json -> git push -> dashboard auto-deploys
  - Every 1 hour : compile full report (with outbox content + tasks) -> cerebronn inbox
  - On silence >30 min : nudge the agent (drop file in their inbox)
  - On silence >2h    : Write alert to CHAD_YI inbox (CHAD_YI reports to Caleb)
  - 9AM SGT  : Morning Briefing -> CHAD_YI inbox (CHAD_YI reports to Caleb)
  - 10PM SGT : Evening Digest   -> CHAD_YI inbox (CHAD_YI reports to Caleb)

COMMUNICATION FLOW:
  Helios writes to CHAD_YI inbox
    ↓
  CHAD_YI reads, compiles, filters
    ↓
  CHAD_YI reports to Caleb (Telegram)

Helios NEVER sends Telegram messages directly to Caleb.

Chad talks to Helios by dropping a .md, .json, or .txt file in:
  /home/chad-yi/.openclaw/workspace/agents/helios/inbox/
Helios writes back to:
  /home/chad-yi/.openclaw/workspace/agents/chad-yi/inbox/
"""

import json
import os
import subprocess
import time
import uuid
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

WORKSPACE        = Path("/home/chad-yi/.openclaw/workspace")
AGENTS_DIR       = WORKSPACE / "agents"
CEREBRONN_INBOX  = AGENTS_DIR / "cerebronn" / "inbox"
CHAD_INBOX       = AGENTS_DIR / "chad-yi" / "inbox"
HELIOS_INBOX     = AGENTS_DIR / "helios" / "inbox"
DASHBOARD_REPO   = WORKSPACE / "mission-control-dashboard"
DASHBOARD_DATA   = DASHBOARD_REPO / "data.json"
ACTIVE_MD        = WORKSPACE / "ACTIVE.md"
HELIOS_API       = os.environ.get("HELIOS_API_URL", "https://helios-api-xfvi.onrender.com")

# Fallback list only. Real watched agents should be derived dynamically from ACTIVE.md
# and the actual agent directories so the infrastructure scales when new agents are added.
DEFAULT_WATCH_AGENTS = ["cerebronn", "forger"]

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8693482792:AAGNa21qo-fNGuPSDE5j5-828QAn7JSubdU")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "8583017204")

AUDIT_INTERVAL      = 15 * 60    # 15 minutes
REPORT_INTERVAL     = 60 * 60    # 1 hour
SILENCE_LIMIT       = 30 * 60    # 30 min = nudge threshold
SILENCE_ALERT_LIMIT = 2 * 60 * 60  # 2 hours = Telegram alert threshold

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)
log = logging.getLogger("helios-v2")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def now_sgt() -> datetime:
    sgt = timezone(timedelta(hours=8))
    return datetime.now(sgt)

def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str))

def write_md(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)

def ms() -> int:
    return int(time.time() * 1000)

# ---------------------------------------------------------------------------
# ACTIVE.md parser
# ---------------------------------------------------------------------------

def parse_active_md() -> dict:
    """Parse ACTIVE.md → returns {tasks, agents, summary}."""
    result: dict = {"tasks": {}, "agents": {}, "summary": {}}
    if not ACTIVE_MD.exists():
        log.warning("  [active.md] File not found")
        return result
    try:
        lines = ACTIVE_MD.read_text().splitlines()
    except Exception as e:
        log.warning(f"  [active.md] Read error: {e}")
        return result

    current_section = ""
    section_map = {
        "CRITICAL": "critical", "URGENT": "urgent",
        "ACTIVE": "active", "IN REVIEW": "review", "DONE": "done", "PENDING": "pending"
    }
    in_agent_table = False
    in_task_table = False

    for i, line in enumerate(lines):
        # Detect section headings
        upper = line.upper()
        for label, prio in section_map.items():
            if label in upper and line.startswith("#"):
                current_section = prio
                in_agent_table = False
                in_task_table = False
                break
        
        # Detect Agent Status table
        if "AGENT STATUS" in upper and line.startswith("#"):
            in_agent_table = True
            in_task_table = False
            current_section = ""
            continue

        # Any other heading ends agent-table parsing
        if line.startswith("#") and in_agent_table and "AGENT STATUS" not in upper:
            in_agent_table = False

        # Detect task tables (sections with task rows)
        if current_section and not in_agent_table:
            # Check if next lines contain task-like rows
            in_task_table = True

        if not line.startswith("|"):
            continue
            
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 2:
            continue
            
        first = cols[0]
        if not first or first.startswith("-") or first in ("ID", "Agent", "**Agent**"):
            continue

        if in_agent_table:
            # | **chad-yi** | **active** | Task... | Notes |
            agent_name = first.replace("**", "").strip().lower()
            status_col = cols[1].replace("**", "").strip().lower() if len(cols) > 1 else ""
            current_task = cols[2].replace("**", "").strip() if len(cols) > 2 else ""
            
            # Extract status (first word before any description)
            status = "offline"  # default
            if status_col:
                if status_col.startswith("active"):
                    status = "active"
                elif status_col.startswith("idle"):
                    status = "idle"
                elif status_col.startswith("blocked"):
                    status = "blocked"
                elif status_col.startswith("offline"):
                    status = "offline"
            
            if agent_name and len(agent_name) < 30 and not agent_name.startswith("-"):
                result["agents"][agent_name] = {
                    "status": status,
                    "currentTask": current_task
                }
                log.info(f"  [active.md] Agent: {agent_name} = {status}")
                
        elif in_task_table and current_section:
            # | A1-6 | Sign contract | CHAD_YI | 2026-03-02 | **BLOCKED** - Due... |
            task_id = first.replace("**", "").strip()
            
            # Skip non-task rows (like "-", "No pending tasks", etc.)
            if not task_id or task_id in ("-", "_") or not ("-" in task_id and len(task_id) < 15):
                continue
                
            title = cols[1].replace("**", "").strip() if len(cols) > 1 else ""
            owner = cols[2].replace("**", "").strip() if len(cols) > 2 else ""
            status_col = cols[-1].upper() if len(cols) > 4 else ""
            
            # Extract status from last column (handles **BLOCKED** - description)
            status = "pending"  # default
            if "BLOCKED" in status_col:
                status = "blocked"
            elif "PROGRESS" in status_col:
                status = "active"
            elif "DONE" in status_col:
                status = "done"
            elif "REVIEW" in status_col:
                status = "review"
            elif current_section == "done":
                status = "done"
            elif current_section == "review":
                status = "review"
            elif current_section == "active":
                status = "active"
            elif current_section in ["critical", "urgent"]:
                status = "blocked"
            
            result["tasks"][task_id] = {
                "id": task_id, 
                "title": title,
                "agent": owner,
                "priority": current_section, 
                "status": status,
            }
            log.info(f"  [active.md] Task: {task_id} = {status}")

    # Calculate summary
    s = result["tasks"]
    result["summary"] = {
        "critical": sum(1 for t in s.values() if t["priority"] == "critical" and t["status"] != "done"),
        "urgent":   sum(1 for t in s.values() if t["priority"] == "urgent" and t["status"] != "done"),
        "active":   sum(1 for t in s.values() if t["status"] == "active"),
        "blocked":  sum(1 for t in s.values() if t["status"] == "blocked"),
        "done":     sum(1 for t in s.values() if t["status"] == "done"),
    }
    
    sm = result["summary"]
    log.info(f"  [active.md] Parsed: {len(result['agents'])} agents, {len(s)} tasks")
    log.info(f"  [active.md] Summary: {sm['critical']} critical, {sm['urgent']} urgent, {sm['active']} active, {sm['blocked']} blocked, {sm['done']} done")
    return result


def get_watch_agents(active_data: dict | None = None) -> list[str]:
    """Derive watched agents dynamically from ACTIVE.md + real directories."""
    if active_data is None:
        active_data = parse_active_md()

    watched: list[str] = []
    for name in active_data.get("agents", {}).keys():
        agent_name = name.strip().lower()
        if agent_name in {"helios", "metric", "summary"}:
            continue
        if (AGENTS_DIR / agent_name).exists():
            watched.append(agent_name)

    if not watched:
        watched = [n for n in DEFAULT_WATCH_AGENTS if (AGENTS_DIR / n).exists()]

    return sorted(set(watched))


def read_agent_outboxes(active_data: dict | None = None) -> dict:
    """Return latest outbox snippet for each watched agent."""
    outboxes: dict = {}
    for name in get_watch_agents(active_data) + ["helios"]:
        outbox = AGENTS_DIR / name / "outbox"
        if not outbox.exists():
            continue
        files = sorted(
            list(outbox.glob("*.json")) + list(outbox.glob("*.md")),
            key=lambda f: f.stat().st_mtime, reverse=True
        )
        if files:
            try:
                outboxes[name] = {"file": files[0].name,
                                  "content": files[0].read_text()[:500]}
            except Exception:
                pass
    return outboxes


# ---------------------------------------------------------------------------
# Helios API
# ---------------------------------------------------------------------------

def post_heartbeat() -> bool:
    if not HAS_REQUESTS:
        return False
    try:
        r = requests.post(
            f"{HELIOS_API}/api/heartbeat",
            json={"agent": "helios", "ts": now_iso()},
            timeout=15,
        )
        if r.status_code == 200:
            log.info("+ Helios API heartbeat accepted")
            return True
        log.warning(f"Helios API heartbeat returned {r.status_code}")
        return False
    except Exception as e:
        log.warning(f"Helios API unreachable: {e}")
        return False

def send_telegram(text: str) -> bool:
    """Send a message to Chad via Telegram."""
    if not HAS_REQUESTS or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    try:
        r = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"},
            timeout=10,
        )
        if r.status_code == 200:
            log.info("  [telegram] Message sent to Chad")
            return True
        log.warning(f"  [telegram] Send failed: {r.status_code} {r.text[:120]}")
        return False
    except Exception as e:
        log.warning(f"  [telegram] Error: {e}")
        return False


def post_event(event_type: str, payload: dict) -> bool:
    if not HAS_REQUESTS:
        return False
    try:
        r = requests.post(
            f"{HELIOS_API}/api/events",
            json={
                "agent": "helios",
                "event_type": event_type,
                "status": "success",
                "idempotency_key": str(uuid.uuid4()),
                "payload": payload,
                "model_tier": "cheap",
                "model_id": "helios-v2-local",
                "reasoning_summary": "",
                "confidence": 1.0,
                "ts": now_iso(),
            },
            timeout=15,
        )
        return r.status_code == 200
    except Exception:
        return False

# ---------------------------------------------------------------------------
# Agent auditing
# ---------------------------------------------------------------------------

def check_agent(name: str) -> dict:
    base = AGENTS_DIR / name
    status = {
        "agent": name,
        "checked_at": now_iso(),
        "has_inbox": (base / "inbox").exists(),
        "has_outbox": (base / "outbox").exists(),
        "outbox_files": 0,
        "inbox_pending": 0,
        "last_activity": None,
        "health": "unknown",
    }

    if (base / "outbox").exists():
        files = list((base / "outbox").glob("*.json")) + list((base / "outbox").glob("*.md"))
        status["outbox_files"] = len(files)
        if files:
            latest = max(files, key=lambda f: f.stat().st_mtime)
            mtime = datetime.fromtimestamp(latest.stat().st_mtime, tz=timezone.utc)
            status["last_activity"] = mtime.isoformat()
            age = (datetime.now(timezone.utc) - mtime).total_seconds()
            status["health"] = "active" if age < SILENCE_LIMIT else "silent"
        else:
            status["health"] = "idle"

    if (base / "inbox").exists():
        pending = [f for f in (base / "inbox").glob("*.json") if "processed" not in str(f)]
        pending += [f for f in (base / "inbox").glob("*.md") if "processed" not in str(f)]
        status["inbox_pending"] = len(pending)

    state_file = base / "state.json"
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text())
            status["state"] = state
            status["health"] = state.get("status", status["health"])
        except Exception:
            pass

    return status

def nudge_agent(name: str, reason: str) -> None:
    nudge_path = AGENTS_DIR / name / "inbox" / f"nudge-{ms()}.md"
    nudge_path.parent.mkdir(parents=True, exist_ok=True)
    write_md(nudge_path, f"""# NUDGE from Helios
**Time:** {now_sgt().strftime('%Y-%m-%d %H:%M SGT')}
**Reason:** {reason}

Helios has noticed you have been quiet. Are you stuck? Any blockers?
Update your outbox with a status report when done.

- Helios
""")
    log.info(f"  Nudge sent -> {name}: {reason}")

# ---------------------------------------------------------------------------
# Inbox reader - Chad/Cerebronn can talk to Helios
# ---------------------------------------------------------------------------

def process_chad_outbox() -> None:
    """Read messages Chad-yi agent left in its outbox, ack them, move to processed."""
    chad_outbox = AGENTS_DIR / "chad-yi" / "outbox"
    if not chad_outbox.exists():
        return
    messages = [
        f for f in list(chad_outbox.glob("*.json")) + list(chad_outbox.glob("*.md"))
        if "processed" not in f.name
    ]
    for msg_file in messages:
        try:
            content = msg_file.read_text()[:800]
            log.info(f"  [chad-outbox] Reading: {msg_file.name}")
            ack_path = CHAD_INBOX / f"helios-read-{ms()}.md"
            CHAD_INBOX.mkdir(parents=True, exist_ok=True)
            write_md(ack_path, f"""# Helios Read Your Outbox Message
**Time:** {now_sgt().strftime('%Y-%m-%d %H:%M SGT')}
**File:** {msg_file.name}

Helios has read and acknowledged this message.

Content preview:
```
{content}
```

- Helios
""")
            msg_file.rename(msg_file.parent / f"processed-{msg_file.name}")
            log.info(f"  [chad-outbox] Processed: {msg_file.name}")
        except Exception as e:
            log.warning(f"  [chad-outbox] Error: {msg_file.name}: {e}")


def process_helios_inbox() -> None:
    if not HELIOS_INBOX.exists():
        return
    messages = [
        f for f in (
            list(HELIOS_INBOX.glob("*.md")) +
            list(HELIOS_INBOX.glob("*.json")) +
            list(HELIOS_INBOX.glob("*.txt"))
        )
        if "processed" not in f.name
    ]
    for msg_file in messages:
        try:
            log.info(f"  [inbox] Processing: {msg_file.name}")
            ack_path = CHAD_INBOX / f"helios-ack-{ms()}.md"
            CHAD_INBOX.mkdir(parents=True, exist_ok=True)
            write_md(ack_path, f"""# Helios Received Your Message
**Time:** {now_sgt().strftime('%Y-%m-%d %H:%M SGT')}
**File:** {msg_file.name}

Message received. Helios is running. Next audit in <15 min.

System status:
- Helios: RUNNING
- Dashboard: https://red-sun-mission-control.onrender.com (updates every 15 min)
- Edit tasks at: /home/chad-yi/mission-control-workspace/ACTIVE.md

- Helios
""")
            msg_file.rename(msg_file.parent / f"processed-{msg_file.name}")
            log.info(f"  [inbox] Acked: {msg_file.name}")
            # DISABLED: Direct Telegram to Caleb. Helios routes through CHAD_YI only.
            # Write acknowledgment to CHAD_YI inbox instead
            ack_file = CHAD_INBOX / f"helios-ack-{ms()}.md"
            write_md(ack_file,
                f"# Helios Acknowledgment\n\n"
                f"**Received:** {msg_file.name}\n"
                f"**Time:** {now_sgt().strftime('%Y-%m-%d %H:%M SGT')}\n\n"
                f"Next dashboard sync in <15 min.\n"
            )
            log.info(f"  [inbox] Wrote ack to chad-yi inbox: {ack_file.name}")
        except Exception as e:
            log.warning(f"  [inbox] Error processing {msg_file.name}: {e}")

# ---------------------------------------------------------------------------
# Report building
# ---------------------------------------------------------------------------

def build_agent_report() -> dict:
    active_data = parse_active_md()
    watched_agents = get_watch_agents(active_data)

    report = {
        "generated_at": now_iso(),
        "generated_by": "helios-v2",
        "watched_agents": watched_agents,
        "agents": {},
        "alerts": [],
        "summary": "",
    }

    for name in watched_agents:
        status = check_agent(name)
        report["agents"][name] = status
        if status["health"] == "silent":
            silence_secs = 0.0
            if status["last_activity"]:
                try:
                    last = datetime.fromisoformat(status["last_activity"])
                    silence_secs = (datetime.now(timezone.utc) - last).total_seconds()
                except Exception:
                    pass
            status["silence_seconds"] = silence_secs
            nudge_agent(name, f"No activity in outbox for >{SILENCE_LIMIT//60} min")
            report["alerts"].append({
                "type": "agent_silent",
                "agent": name,
                "last_activity": status["last_activity"],
                "silence_hours": round(silence_secs / 3600, 1),
                "needs_telegram_alert": silence_secs >= SILENCE_ALERT_LIMIT,
            })

    active = [n for n, s in report["agents"].items() if s["health"] == "active"]
    idle   = [n for n, s in report["agents"].items() if s["health"] == "idle"]
    silent = [n for n, s in report["agents"].items() if s["health"] == "silent"]
    report["summary"] = (
        f"{len(active)} active, {len(idle)} idle, {len(silent)} silent. "
        f"Alerts: {len(report['alerts'])}."
    )
    return report

# ---------------------------------------------------------------------------
# Dashboard sync - THE CORE JOB
# ---------------------------------------------------------------------------

def sync_dashboard_data(report: dict) -> None:
    if not DASHBOARD_DATA.exists():
        log.warning(f"  [sync] data.json not found at {DASHBOARD_DATA}")
        return

    try:
        data = json.loads(DASHBOARD_DATA.read_text())
    except Exception as e:
        log.error(f"  [sync] Failed to read data.json: {e}")
        return

    sgt_now = now_sgt()
    data["lastUpdated"] = sgt_now.isoformat()
    data["updatedBy"] = "helios-v2"

    # Merge task statuses from ACTIVE.md
    active_data = parse_active_md()
    if active_data["tasks"] and "tasks" in data:
        for task_id, task_info in active_data["tasks"].items():
            if task_id in data["tasks"]:
                data["tasks"][task_id]["status"] = task_info["status"]
        data["taskSummary"] = active_data["summary"]

    health_to_status = {
        "active":  "active",
        "idle":    "idle",
        "silent":  "offline",
        "unknown": "offline",
    }

    if "agents" not in data:
        data["agents"] = {}

    agent_names = set(report["agents"].keys()) | set(active_data.get("agents", {}).keys())
    agent_names.discard("helios")

    for agent_name in sorted(agent_names):
        agent_info = report["agents"].get(agent_name, {})
        declared_status = active_data.get("agents", {}).get(agent_name, {}).get("status")
        health = agent_info.get("health", "unknown")
        last_activity = agent_info.get("last_activity")
        if agent_name not in data["agents"]:
            data["agents"][agent_name] = {}
        data["agents"][agent_name]["status"] = declared_status or health_to_status.get(health, "offline")
        if last_activity:
            data["agents"][agent_name]["lastActive"] = last_activity

    if "helios" not in data["agents"]:
        data["agents"]["helios"] = {}
    data["agents"]["helios"]["status"] = "active"
    data["agents"]["helios"]["lastActive"] = sgt_now.isoformat()

    try:
        DASHBOARD_DATA.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        log.info(f"  [sync] data.json written — {data['lastUpdated']}")
    except Exception as e:
        log.error(f"  [sync] Failed to write data.json: {e}")
        return

    try:
        subprocess.run(["git", "-C", str(DASHBOARD_REPO), "add", "data.json"],
                       capture_output=True, text=True, timeout=30)
        commit_msg = f"helios: auto-sync {sgt_now.strftime('%Y-%m-%d %H:%M SGT')}"
        result = subprocess.run(
            ["git", "-C", str(DASHBOARD_REPO), "commit", "-m", commit_msg],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            if "nothing to commit" in result.stdout + result.stderr:
                log.info("  [sync] No changes — dashboard already current")
            else:
                log.warning(f"  [sync] git commit failed: {result.stderr.strip()}")
            return
        result = subprocess.run(
            ["git", "-C", str(DASHBOARD_REPO), "push", "origin", "main"],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode == 0:
            log.info("  [sync] PUSHED to GitHub — Render deploying dashboard")
        else:
            log.warning(f"  [sync] git push failed: {result.stderr.strip()}")
    except subprocess.TimeoutExpired:
        log.warning("  [sync] git timed out")
    except Exception as e:
        log.error(f"  [sync] git error: {e}")

# ---------------------------------------------------------------------------
# Hourly reports
# ---------------------------------------------------------------------------

def write_cerebronn_report(report: dict) -> None:
    ts = int(time.time())
    full_report = {
        **report,
        "agent_outboxes": read_agent_outboxes(),
        "tasks_from_active_md": parse_active_md(),
    }
    path = CEREBRONN_INBOX / f"helios-report-{ts}.json"
    CEREBRONN_INBOX.mkdir(parents=True, exist_ok=True)
    write_json(path, full_report)
    log.info(f"  Cerebronn report: {path.name}")

def update_cerebronn_briefing(report: dict) -> None:
    # Cerebronn owns briefing.md — it rewrites from memory every 30min.
    # Helios only writes JSON reports to cerebronn/inbox/.
    # Do NOT write here: it would overwrite Cerebronn's richer version.
    log.info("  [briefing] Skipped — Cerebronn owns briefing.md")

# ---------------------------------------------------------------------------
# Digest — 9AM morning briefing + 10PM evening report
# ---------------------------------------------------------------------------

def build_digest_text(label: str) -> tuple:
    """Build digest as (telegram_short, full_md)."""
    report = build_agent_report()
    active_data = parse_active_md()
    outboxes = read_agent_outboxes()
    sgt = now_sgt()
    date_str = sgt.strftime("%Y-%m-%d")
    time_str = sgt.strftime("%H:%M SGT")

    # Agent section
    agent_md_rows = ""
    tg_agents = ""
    for name, status in report["agents"].items():
        health = status["health"]
        icon = {"active": "\u2705", "idle": "\u26aa", "silent": "\u26a0\ufe0f"}.get(health, "\u26aa")
        snippet = outboxes.get(name, {}).get("content", "")[:80].strip().replace("\n", " ")
        agent_md_rows += f"| {icon} {name} | {health} | {snippet} |\n"
        tg_agents += f"{icon} {name}: {health}\n"

    # Task section — skip done tasks
    task_md_rows = ""
    tg_needs_attention = ""
    for task_id, task in active_data["tasks"].items():
        if task["status"] == "done":
            continue
        picon = {
            "critical": "\U0001f534", "urgent": "\U0001f7e1",
            "blocked": "\u26d4", "review": "\U0001f4cc", "active": "\U0001f7e2",
        }.get(task["priority"], "\u26aa")
        task_md_rows += f"| {picon} {task_id} | {task['title']} | {task['agent']} | {task['status']} |\n"
        if task["priority"] in ("critical", "urgent", "blocked"):
            tg_needs_attention += f"{picon} {task_id}: {task['title']}\n"

    sm = active_data["summary"]
    summary_line = (f"{sm.get('critical',0)} crit, {sm.get('urgent',0)} urgent, "
                    f"{sm.get('active',0)} active, {sm.get('blocked',0)} blocked")

    tg_text = (
        f"{'🌞' if 'Morning' in label else '🌙'} *{label} — {date_str}*\n"
        f"_{time_str}_\n\n"
        f"*Agents:*\n{tg_agents}\n"
        f"*Tasks:* {summary_line}\n"
        + (f"\n*Needs attention:*\n{tg_needs_attention}" if tg_needs_attention else "") +
        f"\nDashboard: https://red-sun-mission-control.onrender.com"
    )

    full_md = f"""# {label} — {date_str}
Generated: {time_str} by Helios

## Agents
| Agent | Health | Latest Output |
|-------|--------|---------------|
{agent_md_rows.rstrip()}
| helios | active | running |

## Tasks ({summary_line})
| # | Title | Owner | Status |
|---|-------|-------|--------|
{task_md_rows.rstrip() or "| — | No tasks parsed | — | — |"}

Dashboard: https://red-sun-mission-control.onrender.com
Edit tasks: {ACTIVE_MD}
"""
    return tg_text, full_md


def send_digest(label: str) -> None:
    tg_text, full_md = build_digest_text(label)
    ts = int(time.time())
    path = CHAD_INBOX / f"digest-{ts}.md"
    CHAD_INBOX.mkdir(parents=True, exist_ok=True)
    write_md(path, full_md)
    CEREBRONN_INBOX.mkdir(parents=True, exist_ok=True)
    write_md(CEREBRONN_INBOX / f"digest-{ts}.md", full_md)
    # DISABLED: Direct Telegram to Caleb. Route through CHAD_YI only.
    # CHAD_YI will read digest from inbox and report to Caleb.
    log.info(f"  Digest sent to chad-yi inbox: {label}")

# ---------------------------------------------------------------------------
# Main loop - runs forever
# ---------------------------------------------------------------------------

def main() -> None:
    log.info("=" * 60)
    log.info("HELIOS V2 - Mission Control Engineer - STARTING")
    log.info(f"  Workspace:      {WORKSPACE}")
    log.info(f"  Helios API:     {HELIOS_API}")
    log.info(f"  Dashboard repo: {DASHBOARD_REPO}")
    log.info(f"  Audit interval: {AUDIT_INTERVAL}s (15 min)")
    log.info(f"  Chad inbox:     {CHAD_INBOX}")
    log.info(f"  Helios inbox:   {HELIOS_INBOX}")
    log.info("=" * 60)

    last_audit  = 0.0
    last_report = 0.0
    morning_sent_today = ""
    evening_sent_today = ""
    alerted_agents: set = set()  # agents already Telegram-alerted for 2h silence

    # Boot sequence
    post_heartbeat()
    post_event("agent_update", {"status": "started", "version": "2.0"})
    log.info("Boot: running startup audit + dashboard sync...")
    boot_report = build_agent_report()
    log.info(f"  {boot_report['summary']}")
    sync_dashboard_data(boot_report)
    write_cerebronn_report(boot_report)
    update_cerebronn_briefing(boot_report)
    last_audit  = time.time()
    last_report = time.time()
    # DISABLED: Direct Telegram to Caleb. Helios routes through CHAD_YI only.
    # Write boot notification to CHAD_YI inbox instead.
    boot_file = CHAD_INBOX / f"helios-boot-{int(time.time())}.md"
    write_md(boot_file,
        f"# Helios Online\n\n"
        f"**Time:** {now_sgt().strftime('%Y-%m-%d %H:%M SGT')}\n"
        f"**Status:** {boot_report['summary']}\n\n"
        f"Helios is running and monitoring agents."
    )
    log.info(f"  Boot notification written to chad-yi inbox")

    while True:
        now    = time.time()
        now_dt = now_sgt()

        # Check Helios inbox (Chad talking to Helios) + chad-yi outbox
        process_helios_inbox()
        process_chad_outbox()

        # Every 15 min: audit + heartbeat + dashboard sync
        if now - last_audit >= AUDIT_INTERVAL:
            log.info("Running audit...")
            report = build_agent_report()
            log.info(f"  {report['summary']}")
            post_heartbeat()
            post_event("agent_update", {
                "summary": report["summary"],
                "alert_count": len(report["alerts"])
            })
            sync_dashboard_data(report)
            last_audit = now

            # Telegram alert for agents silent >2h (once per agent until they recover)
            # DISABLED: Direct Telegram to Caleb. Route through CHAD_YI instead.
            for alert in report["alerts"]:
                if alert.get("needs_telegram_alert") and alert["agent"] not in alerted_agents:
                    # Write alert to CHAD_YI inbox
                    alert_file = CHAD_INBOX / f"helios-alert-{alert['agent']}-{int(time.time())}.md"
                    write_md(alert_file,
                        f"# Agent Silent Alert\n\n"
                        f"**Agent:** {alert['agent']}\n"
                        f"**Last seen:** {alert.get('last_activity', 'unknown')}\n"
                        f"**Silent for:** {alert.get('silence_hours', '?')}h\n\n"
                        f"Check their outbox or assign a new task."
                    )
                    alerted_agents.add(alert["agent"])
                    log.info(f"  [alert] Written to chad-yi inbox — silent agent: {alert['agent']}")
            # Clear alert for agents that recovered
            for name, status in report["agents"].items():
                if status["health"] != "silent" and name in alerted_agents:
                    alerted_agents.discard(name)

            if now - last_report >= REPORT_INTERVAL:
                write_cerebronn_report(report)
                update_cerebronn_briefing(report)
                last_report = now

        today_str = now_dt.strftime("%Y-%m-%d")

        # 9 AM SGT morning briefing
        if now_dt.hour == 9 and morning_sent_today != today_str:
            log.info("Sending morning briefing...")
            send_digest("Morning Briefing")
            morning_sent_today = today_str

        # 10 PM SGT evening digest
        if now_dt.hour == 22 and evening_sent_today != today_str:
            log.info("Sending evening digest...")
            send_digest("Evening Digest")
            evening_sent_today = today_str

        time.sleep(60)


if __name__ == "__main__":
    main()
