#!/usr/bin/env python3
"""
gws-agent.py — Google Workspace Agent
Handles Gmail, Drive, Calendar, Sheets, Docs via gws CLI

Communication:
  Reads tasks from: inbox/
  Writes results to: outbox/
  Logs to: logs/gws-agent.log
"""

import json
import os
import subprocess
import time
import logging
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

WORKSPACE    = Path("/home/chad-yi/.openclaw/workspace")
AGENT_DIR    = WORKSPACE / "agents" / "gws-agent"
INBOX        = AGENT_DIR / "inbox"
OUTBOX       = AGENT_DIR / "outbox"
LOG_FILE     = AGENT_DIR / "logs" / "gws-agent.log"

POLL_INTERVAL = 30  # seconds

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("gws-agent")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def write_result(task_id, success, data, error=None):
    """Write result to outbox"""
    result = {
        "task_id": task_id,
        "timestamp": now_iso(),
        "success": success,
        "data": data
    }
    if error:
        result["error"] = error
    
    out_path = OUTBOX / f"{task_id}.json"
    out_path.write_text(json.dumps(result, indent=2))
    log.info(f"Wrote result: {out_path}")

def run_gws(args):
    """Execute gws command"""
    cmd = ["gws"] + args
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Command timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ---------------------------------------------------------------------------
# Task Handlers
# ---------------------------------------------------------------------------

def handle_gmail_list(task):
    """List emails from Gmail"""
    limit = task.get("limit", 10)
    label = task.get("label", "")
    
    cmd = ["gmail", "list", "--limit", str(limit), "--json"]
    if label:
        cmd.extend(["--label", label])
    
    result = run_gws(cmd)
    
    if result["success"]:
        try:
            emails = json.loads(result["stdout"])
            return True, {"emails": emails, "count": len(emails)}
        except:
            return True, {"raw": result["stdout"]}
    else:
        return False, None, result.get("stderr", "Failed to list emails")

def handle_gmail_send(task):
    """Send email via Gmail"""
    to = task.get("to")
    subject = task.get("subject")
    body = task.get("body", "")
    
    if not to or not subject:
        return False, None, "Missing 'to' or 'subject'"
    
    cmd = ["gmail", "send", "--to", to, "--subject", subject, "--body", body]
    
    result = run_gws(cmd)
    
    if result["success"]:
        return True, {"sent_to": to, "subject": subject}, None
    else:
        return False, None, result.get("stderr", "Failed to send")

def handle_drive_list(task):
    """List files in Google Drive"""
    folder = task.get("folder", "")
    
    cmd = ["drive", "list", "--json"]
    if folder:
        cmd.extend(["--folder", folder])
    
    result = run_gws(cmd)
    
    if result["success"]:
        try:
            files = json.loads(result["stdout"])
            return True, {"files": files, "count": len(files)}, None
        except:
            return True, {"raw": result["stdout"]}, None
    else:
        return False, None, result.get("stderr")

def handle_drive_upload(task):
    """Upload file to Drive"""
    local_path = task.get("local_path")
    folder = task.get("folder", "")
    
    if not local_path:
        return False, None, "Missing 'local_path'"
    
    cmd = ["drive", "upload", local_path]
    if folder:
        cmd.extend(["--folder", folder])
    
    result = run_gws(cmd)
    
    if result["success"]:
        return True, {"uploaded": local_path}, None
    else:
        return False, None, result.get("stderr")

def handle_sheets_read(task):
    """Read from Google Sheets"""
    sheet_id = task.get("sheet_id")
    range_name = task.get("range", "")
    
    if not sheet_id:
        return False, None, "Missing 'sheet_id'"
    
    cmd = ["sheets", "get", sheet_id]
    if range_name:
        cmd.extend(["--range", range_name])
    cmd.append("--json")
    
    result = run_gws(cmd)
    
    if result["success"]:
        try:
            data = json.loads(result["stdout"])
            return True, {"data": data}, None
        except:
            return True, {"raw": result["stdout"]}, None
    else:
        return False, None, result.get("stderr")

def handle_sheets_append(task):
    """Append row to Google Sheets"""
    sheet_id = task.get("sheet_id")
    values = task.get("values", [])
    
    if not sheet_id or not values:
        return False, None, "Missing 'sheet_id' or 'values'"
    
    values_str = ",".join(values)
    cmd = ["sheets", "append", sheet_id, "--sheet", "Sheet1", "--values", values_str]
    
    result = run_gws(cmd)
    
    if result["success"]:
        return True, {"appended": values}, None
    else:
        return False, None, result.get("stderr")

def handle_calendar_list(task):
    """List calendar events"""
    cmd = ["calendar", "events", "list", "--json"]
    
    result = run_gws(cmd)
    
    if result["success"]:
        try:
            events = json.loads(result["stdout"])
            return True, {"events": events, "count": len(events)}, None
        except:
            return True, {"raw": result["stdout"]}, None
    else:
        return False, None, result.get("stderr")

# ---------------------------------------------------------------------------
# Task Router
# ---------------------------------------------------------------------------

HANDLERS = {
    "GMAIL_LIST": handle_gmail_list,
    "GMAIL_SEND": handle_gmail_send,
    "DRIVE_LIST": handle_drive_list,
    "DRIVE_UPLOAD": handle_drive_upload,
    "SHEETS_READ": handle_sheets_read,
    "SHEETS_APPEND": handle_sheets_append,
    "CALENDAR_LIST": handle_calendar_list,
}

def process_task(task_file):
    """Process a single task file"""
    log.info(f"Processing: {task_file.name}")
    
    try:
        task = json.loads(task_file.read_text())
        task_id = task.get("id", task_file.stem)
        task_type = task.get("type")
        
        handler = HANDLERS.get(task_type)
        if not handler:
            write_result(task_id, False, None, f"Unknown task type: {task_type}")
            return
        
        result = handler(task)
        
        if len(result) == 3:
            success, data, error = result
        else:
            success, data = result
            error = None
        
        write_result(task_id, success, data, error)
        
        # Delete processed task
        task_file.unlink()
        log.info(f"Completed: {task_id}")
        
    except Exception as e:
        log.error(f"Failed to process {task_file}: {e}")
        write_result(task_file.stem, False, None, str(e))
        task_file.unlink()

# ---------------------------------------------------------------------------
# Main Loop
# ---------------------------------------------------------------------------

def main():
    log.info("=" * 50)
    log.info("Google Workspace Agent Starting")
    log.info(f"Inbox: {INBOX}")
    log.info(f"Outbox: {OUTBOX}")
    log.info("=" * 50)
    
    # Ensure directories exist
    INBOX.mkdir(parents=True, exist_ok=True)
    OUTBOX.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    while True:
        try:
            # Check for tasks
            tasks = list(INBOX.glob("*.json"))
            
            for task_file in tasks:
                process_task(task_file)
            
            if tasks:
                log.info(f"Processed {len(tasks)} task(s)")
            
            time.sleep(POLL_INTERVAL)
            
        except KeyboardInterrupt:
            log.info("Shutting down...")
            break
        except Exception as e:
            log.error(f"Main loop error: {e}")
            time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
