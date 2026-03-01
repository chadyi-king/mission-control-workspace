#!/usr/bin/env python3
"""
forger.py — Forger Heartbeat Script
The Website Builder Agent. Manages build queue and tracks site delivery.

What this script does (NO LLM - pure Python watchdog):
  - Polls inbox/ every 15 minutes for new build briefs (.md files)
  - Parses briefs → adds jobs to build-queue.json
  - Monitors builds/ directory for completed website files
  - Notifies Chad when a build needs review or is ready to deploy
  - Writes heartbeat.json every cycle for Helios/Cerebronn visibility
  - Archives processed inbox files

The actual website CODE generation happens when Forger (as an OpenClaw agent)
is invoked by Chad — that's when the LLM runs. This script just tracks the queue.

INBOX  (Chad/Helios drop briefs here):
  /home/chad-yi/.openclaw/workspace/agents/forger/inbox/

BUILDS (Forger outputs website files here):
  /home/chad-yi/.openclaw/workspace/agents/forger/builds/{company-slug}/

QUEUE  (persistent build state):
  /home/chad-yi/.openclaw/agents/forger/memory/build-queue.json
"""

import json
import os
import re
import time
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
WORKSPACE       = Path("/home/chad-yi/.openclaw/workspace")
AGENT_HOME      = Path("/home/chad-yi/.openclaw/agents/forger")
MEMORY          = AGENT_HOME / "memory"
INBOX           = WORKSPACE / "agents" / "forger" / "inbox"
OUTBOX          = WORKSPACE / "agents" / "forger" / "outbox"
BUILDS          = WORKSPACE / "agents" / "forger" / "builds"
TEMPLATES       = WORKSPACE / "agents" / "forger" / "templates"
CHAD_INBOX      = WORKSPACE / "agents" / "chad-yi" / "inbox"
HELIOS_INBOX    = WORKSPACE / "agents" / "helios" / "inbox"
CEREBRONN_INBOX = WORKSPACE / "agents" / "cerebronn" / "inbox"
ARCHIVE         = MEMORY / "archive"

QUEUE_FILE      = MEMORY / "build-queue.json"
HEARTBEAT_FILE  = WORKSPACE / "agents" / "forger" / "heartbeat.json"

SLEEP_INTERVAL  = 15 * 60   # 15 minutes

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(WORKSPACE / "agents" / "forger" / "forger.log"),
    ]
)
log = logging.getLogger("forger")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sgt_now() -> datetime:
    return datetime.now(timezone(timedelta(hours=8)))

def sgt_str(dt: datetime = None) -> str:
    dt = dt or sgt_now()
    return dt.strftime("%Y-%m-%d %H:%M SGT")

def ts() -> int:
    return int(time.time())

def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}

def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2))

def write_md(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)

def archive_file(f: Path) -> None:
    dest = ARCHIVE / sgt_now().strftime("%Y-%m") / f.name
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        f.rename(dest)
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Build Queue
# ---------------------------------------------------------------------------

def load_queue() -> dict:
    """Load or initialise the build queue."""
    q = read_json(QUEUE_FILE)
    if not q:
        q = {
            "builds": {},       # slug → build record
            "updated_at": sgt_str(),
        }
    return q

def save_queue(q: dict) -> None:
    q["updated_at"] = sgt_str()
    write_json(QUEUE_FILE, q)


def queue_summary(q: dict) -> str:
    builds = q.get("builds", {})
    if not builds:
        return "No builds in queue."
    counts = {}
    for b in builds.values():
        s = b.get("status", "unknown")
        counts[s] = counts.get(s, 0) + 1
    parts = [f"{v} {k}" for k, v in counts.items()]
    return "Builds: " + ", ".join(parts)

# ---------------------------------------------------------------------------
# Brief Parser
# ---------------------------------------------------------------------------

def slug(name: str) -> str:
    """Convert company name to URL-safe slug."""
    return re.sub(r"[^a-z0-9-]", "-", name.lower().strip()).strip("-")

def parse_brief(f: Path) -> dict | None:
    """
    Parse a brief .md file. Expected format (loose — tries to extract key fields):

    # Brief: Company Name
    **Domain:** example.com
    **Colors:** #FF0000 (primary), #000000 (secondary)
    **Tone:** professional, modern
    **Pages:** Home, About, Services, Contact
    **Copy:** [copy details or attached]
    **Special:** animations, booking widget, etc.
    """
    try:
        text = f.read_text()
        lines = text.split("\n")

        record = {
            "file": f.name,
            "raw": text[:2000],
            "received_at": sgt_str(),
            "status": "pending",
            "company": "",
            "domain": "",
            "colors": "",
            "tone": "",
            "pages": "",
            "special": "",
            "slug": "",
        }

        for line in lines:
            line = line.strip()
            # Company name from heading
            if line.startswith("# Brief:") or line.startswith("# BRIEF:"):
                record["company"] = line.split(":", 1)[-1].strip()
            elif line.startswith("# ") and not record["company"]:
                record["company"] = line[2:].strip()

            # Key-value pairs
            for key, field in [
                ("domain", "domain"),
                ("url", "domain"),
                ("colors", "colors"),
                ("colour", "colors"),
                ("tone", "tone"),
                ("style", "tone"),
                ("pages", "pages"),
                ("sections", "pages"),
                ("special", "special"),
                ("features", "special"),
                ("animations", "special"),
            ]:
                if line.lower().startswith(f"**{key}") or line.lower().startswith(f"{key}:"):
                    val = line.split(":", 1)[-1].strip().strip("*").strip()
                    if val:
                        record[field] = val

        if not record["company"]:
            # Use filename
            record["company"] = f.stem.replace("-brief", "").replace("brief-", "").replace("-", " ").title()

        record["slug"] = slug(record["company"])
        return record

    except Exception as e:
        log.error(f"[parse] Failed to parse brief {f.name}: {e}")
        return None


# ---------------------------------------------------------------------------
# Build Detection
# ---------------------------------------------------------------------------

def check_build_completion(q: dict) -> list:
    """
    Check builds/ directory. If a build dir has an index.html,
    mark the job as 'ready_for_review'.
    Returns list of newly completed slugs.
    """
    completed = []
    builds = q.get("builds", {})

    for s, record in builds.items():
        if record.get("status") != "in_progress":
            continue
        build_dir = BUILDS / s
        index = build_dir / "index.html"
        if index.exists():
            record["status"] = "ready_for_review"
            record["completed_at"] = sgt_str()
            file_count = len(list(build_dir.rglob("*")))
            record["file_count"] = file_count
            completed.append(s)
            log.info(f"[build] {s} — build complete ({file_count} files)")
    return completed


def check_deployed(q: dict) -> list:
    """Check outbox for deploy-confirm files."""
    deployed = []
    if not OUTBOX.exists():
        return deployed
    for f in OUTBOX.iterdir():
        if f.name.startswith("deployed-") and f.suffix == ".md":
            s = f.stem.replace("deployed-", "")
            if s in q.get("builds", {}):
                q["builds"][s]["status"] = "deployed"
                q["builds"][s]["deployed_at"] = sgt_str()
                deployed.append(s)
                archive_file(f)
                log.info(f"[deploy] {s} — marked as deployed")
    return deployed


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

def notify_chad_new_brief(record: dict) -> None:
    """Tell Chad there's a new website to build."""
    company = record["company"]
    s = record["slug"]
    domain = record.get("domain", "TBD")
    pages = record.get("pages", "TBD")
    special = record.get("special", "none")

    content = f"""# 🔨 Forger: New Build Brief — {company}

**Received:** {record['received_at']}
**Company:** {company}
**Domain:** {domain}
**Slug:** {s}
**Pages:** {pages}
**Special:** {special}

## Action Required
Invoke **Forger** to build this website. Steps:
1. Open Forger agent in OpenClaw
2. Tell Forger: "Build the {company} website from the brief at `agents/forger/inbox/{record['file']}`"
3. Forger will generate files into `agents/forger/builds/{s}/`
4. Review output then confirm deploy

## Full Brief
```
{record['raw'][:500]}
```
"""
    path = CHAD_INBOX / f"forger-brief-{ts()}.md"
    write_md(path, content)
    log.info(f"[notify] Chad notified — new build: {company}")


def notify_chad_build_ready(s: str, record: dict) -> None:
    """Tell Chad a build is ready for review."""
    company = record.get("company", s)
    file_count = record.get("file_count", "?")
    build_dir = BUILDS / s

    content = f"""# ✅ Forger Build Ready — {company}

**Completed:** {record.get('completed_at', sgt_str())}
**Build dir:** `agents/forger/builds/{s}/`
**Files generated:** {file_count}

## Review Checklist
- [ ] Open `builds/{s}/index.html` in browser
- [ ] Check mobile layout
- [ ] Verify brand colors + fonts
- [ ] Replace placeholder images with real assets
- [ ] Test all links + forms

## Deploy When Ready
1. Run: `vercel agents/forger/builds/{s}/ --prod`
2. Assign custom domain in Vercel dashboard
3. Drop a confirmation file: `agents/forger/outbox/deployed-{s}.md`

"""
    path = CHAD_INBOX / f"forger-ready-{ts()}.md"
    write_md(path, content)
    log.info(f"[notify] Chad notified — build ready: {company}")


def notify_cerebronn_status(q: dict) -> None:
    """Write a brief status update to Cerebronn inbox."""
    summary = queue_summary(q)
    content = {
        "source": "forger",
        "timestamp": sgt_str(),
        "summary": summary,
        "builds": {
            s: {"status": b.get("status"), "company": b.get("company")}
            for s, b in q.get("builds", {}).items()
        }
    }
    path = CEREBRONN_INBOX / f"forger-status-{ts()}.json"
    CEREBRONN_INBOX.mkdir(parents=True, exist_ok=True)
    write_json(path, content)
    log.info(f"[cerebronn] Status update sent: {summary}")


# ---------------------------------------------------------------------------
# Heartbeat
# ---------------------------------------------------------------------------

def write_heartbeat(q: dict) -> None:
    builds = q.get("builds", {})
    status = "idle"
    current_task = "Watching for build briefs"
    pending = [s for s, b in builds.items() if b.get("status") == "pending"]
    in_progress = [s for s, b in builds.items() if b.get("status") == "in_progress"]
    ready = [s for s, b in builds.items() if b.get("status") == "ready_for_review"]
    deployed = [s for s, b in builds.items() if b.get("status") == "deployed"]

    if in_progress:
        status = "building"
        current_task = f"Building: {', '.join(in_progress)}"
    elif pending:
        status = "awaiting_build"
        current_task = f"Briefed, awaiting build: {', '.join(pending)}"
    elif ready:
        status = "awaiting_review"
        current_task = f"Ready for review: {', '.join(ready)}"
    elif deployed:
        status = "running"
        current_task = f"{len(deployed)} site(s) live"

    hb = {
        "agent": "forger",
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status,
        "currentTask": current_task,
        "builds_pending": len(pending),
        "builds_in_progress": len(in_progress),
        "builds_ready": len(ready),
        "builds_deployed": len(deployed),
        "blockers": None,
        "log": "agents/forger/forger.log",
    }
    HEARTBEAT_FILE.parent.mkdir(parents=True, exist_ok=True)
    write_json(HEARTBEAT_FILE, hb)


# ---------------------------------------------------------------------------
# Main Cycle
# ---------------------------------------------------------------------------

def run_cycle():
    log.info(f"[cycle] Starting cycle — {sgt_str()}")

    # Ensure dirs
    for d in [INBOX, OUTBOX, BUILDS, TEMPLATES, MEMORY, ARCHIVE, CHAD_INBOX]:
        d.mkdir(parents=True, exist_ok=True)

    q = load_queue()
    new_briefs = 0
    completed = 0

    # 1. Process inbox: new build briefs
    for f in sorted(INBOX.iterdir()):
        if f.suffix != ".md":
            archive_file(f)
            continue

        record = parse_brief(f)
        if not record:
            archive_file(f)
            continue

        s = record["slug"]
        existing = q["builds"].get(s, {})

        if existing.get("status") in ("deployed", "ready_for_review", "in_progress"):
            log.info(f"[inbox] {s} already in queue with status={existing['status']}, skipping")
            archive_file(f)
            continue

        # New or re-submitted brief
        q["builds"][s] = record
        new_briefs += 1
        notify_chad_new_brief(record)
        archive_file(f)
        log.info(f"[brief] Queued new build: {record['company']} ({s})")

    # 2. Check for completed builds
    newly_completed = check_build_completion(q)
    for s in newly_completed:
        notify_chad_build_ready(s, q["builds"][s])
        completed += 1

    # 3. Check for deploy confirmations
    deployed = check_deployed(q)

    # 4. Write heartbeat
    write_heartbeat(q)

    # 5. Send status to Cerebronn every cycle (lightweight JSON)
    notify_cerebronn_status(q)

    # 6. Save queue
    save_queue(q)

    total = len(q.get("builds", {}))
    log.info(
        f"[cycle] Done — {new_briefs} new briefs, {completed} completed, "
        f"{len(deployed)} deployed, {total} total in queue"
    )


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

def main():
    log.info("=" * 60)
    log.info("Forger — Website Builder Agent — STARTED")
    log.info(f"Inbox:  {INBOX}")
    log.info(f"Builds: {BUILDS}")
    log.info(f"Cycle:  {SLEEP_INTERVAL // 60} minutes")
    log.info("=" * 60)

    while True:
        try:
            run_cycle()
        except Exception as e:
            log.error(f"[cycle] Unhandled error: {e}", exc_info=True)

        log.info(f"[sleep] Next cycle in {SLEEP_INTERVAL // 60} minutes")
        time.sleep(SLEEP_INTERVAL)


if __name__ == "__main__":
    main()
