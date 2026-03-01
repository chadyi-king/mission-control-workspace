#!/usr/bin/env python3
"""
helios-v2.py — Helios Local Agent
Runs as a background process. Mission Control Engineer.

Responsibilities (never stops):
  - Every 15 min : audit all agents (check inbox/outbox activity)
  - Every 15 min : POST heartbeat to Helios API
  - Every 15 min : sync live agent status -> data.json -> git push -> dashboard auto-deploys
  - Every 1 hour : compile report -> write to cerebronn inbox + update briefing.md
  - Every 8 PM SGT : write daily digest -> chad-yi inbox
  - On silence >30 min : nudge the agent

Chad talks to Helios by dropping a .md or .json file in:
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
HELIOS_API       = os.environ.get("HELIOS_API_URL", "https://helios-api-xfvi.onrender.com")

WATCH_AGENTS     = ["chad-yi", "escritor", "autour", "quanta", "mensamusa"]

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8693482792:AAGNa21qo-fNGuPSDE5j5-828QAn7JSubdU")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID", "8583017204")

AUDIT_INTERVAL   = 15 * 60   # 15 minutes
REPORT_INTERVAL  = 60 * 60   # 1 hour
SILENCE_LIMIT    = 30 * 60   # 30 minutes = nudge threshold

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

def process_helios_inbox() -> None:
    if not HELIOS_INBOX.exists():
        return
    messages = [
        f for f in list(HELIOS_INBOX.glob("*.md")) + list(HELIOS_INBOX.glob("*.json"))
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
- Edit tasks at: /home/chad-yi/.openclaw/workspace/mission-control-workspace/ACTIVE.md

- Helios
""")
            msg_file.rename(msg_file.parent / f"processed-{msg_file.name}")
            log.info(f"  [inbox] Acked: {msg_file.name}")
            send_telegram(
                f"\u2705 *Helios received your message*\n"
                f"File: `{msg_file.name}`\n"
                f"Time: {now_sgt().strftime('%Y-%m-%d %H:%M SGT')}\n\n"
                f"Next dashboard sync in <15 min.\n"
                f"Dashboard: https://red-sun-mission-control.onrender.com"
            )
        except Exception as e:
            log.warning(f"  [inbox] Error processing {msg_file.name}: {e}")

# ---------------------------------------------------------------------------
# Report building
# ---------------------------------------------------------------------------

def build_agent_report() -> dict:
    report = {
        "generated_at": now_iso(),
        "generated_by": "helios-v2",
        "agents": {},
        "alerts": [],
        "summary": "",
    }

    for name in WATCH_AGENTS:
        status = check_agent(name)
        report["agents"][name] = status
        if status["health"] == "silent":
            nudge_agent(name, f"No activity in outbox for >{SILENCE_LIMIT//60} min")
            report["alerts"].append({
                "type": "agent_silent",
                "agent": name,
                "last_activity": status["last_activity"],
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

    agent_map = {
        "chad-yi":   "chad-yi",
        "escritor":  "escritor",
        "quanta":    "quanta",
        "mensamusa": "mensamusa",
        "autour":    "autour",
    }
    health_to_status = {
        "active":  "active",
        "idle":    "idle",
        "silent":  "offline",
        "unknown": "offline",
    }

    if "agents" not in data:
        data["agents"] = {}

    for helios_name, data_key in agent_map.items():
        agent_info = report["agents"].get(helios_name, {})
        health = agent_info.get("health", "unknown")
        last_activity = agent_info.get("last_activity")
        if data_key not in data["agents"]:
            data["agents"][data_key] = {}
        data["agents"][data_key]["status"] = health_to_status.get(health, "offline")
        if last_activity:
            data["agents"][data_key]["lastActive"] = last_activity

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
    path = CEREBRONN_INBOX / f"helios-report-{ts}.json"
    CEREBRONN_INBOX.mkdir(parents=True, exist_ok=True)
    write_json(path, report)
    log.info(f"  Cerebronn report: {path.name}")

def update_cerebronn_briefing(report: dict) -> None:
    briefing_path = Path("/home/chad-yi/.openclaw/agents/cerebronn/memory/briefing.md")
    agent_rows = ""
    for name, status in report["agents"].items():
        icon = {"active": "OK", "idle": "IDLE", "silent": "SILENT", "unknown": "?"}.get(status["health"], "?")
        last = status.get("last_activity", "-")
        if last and last != "-":
            last = last[:16].replace("T", " ")
        agent_rows += f"| {name} | {last} | {icon} |\n"

    content = f"""# BRIEFING - For Chad (Session Start)
*Auto-updated by Helios every hour. Last: {now_sgt().strftime('%Y-%m-%d %H:%M SGT')}*

## Agent Status
| Agent | Last Active | Status |
|-------|-------------|--------|
{agent_rows.rstrip()}
| helios | now | RUNNING |
| cerebronn | - | RUNNING |

## Summary
{report['summary']}

## Edit Tasks
File: /home/chad-yi/.openclaw/workspace/mission-control-workspace/ACTIVE.md
Helios reads it every 15 min and pushes to dashboard automatically.
"""
    briefing_path.parent.mkdir(parents=True, exist_ok=True)
    briefing_path.write_text(content)
    log.info("  Briefing updated")

# ---------------------------------------------------------------------------
# Daily digest
# ---------------------------------------------------------------------------

def write_daily_digest() -> None:
    report = build_agent_report()
    ts = int(time.time())
    path = CHAD_INBOX / f"daily-digest-{ts}.md"
    CHAD_INBOX.mkdir(parents=True, exist_ok=True)
    agent_lines = ""
    for name, status in report["agents"].items():
        icon = {"active": "OK", "idle": "IDLE", "silent": "SILENT"}.get(status["health"], "?")
        agent_lines += f"- {icon} {name}: {status['health']}\n"
    write_md(path, f"""# Daily Digest - {now_sgt().strftime('%Y-%m-%d')}
Generated: {now_sgt().strftime('%H:%M SGT')} by Helios

## Agent Status
{agent_lines.rstrip()}

## Summary
{report['summary']}

Dashboard: https://red-sun-mission-control.onrender.com
""")
    log.info(f"  Daily digest: {path.name}")

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
    digest_sent_today = ""

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
    send_telegram(
        f"\U0001f7e2 *Helios is online*\n"
        f"Time: {now_sgt().strftime('%Y-%m-%d %H:%M SGT')}\n"
        f"{boot_report['summary']}\n\n"
        f"Dashboard: https://red-sun-mission-control.onrender.com"
    )

    while True:
        now    = time.time()
        now_dt = now_sgt()

        # Check Helios inbox (Chad talking to Helios)
        process_helios_inbox()

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

            if now - last_report >= REPORT_INTERVAL:
                write_cerebronn_report(report)
                update_cerebronn_briefing(report)
                last_report = now

        # 8 PM SGT daily digest
        today_str = now_dt.strftime("%Y-%m-%d")
        if now_dt.hour == 20 and digest_sent_today != today_str:
            log.info("Writing daily digest...")
            write_daily_digest()
            digest_report = build_agent_report()
            send_telegram(
                f"\U0001f4cb *Daily Digest — {today_str}*\n"
                f"{digest_report['summary']}\n\n"
                f"Dashboard: https://red-sun-mission-control.onrender.com"
            )
            digest_sent_today = today_str

        time.sleep(60)


if __name__ == "__main__":
    main()
