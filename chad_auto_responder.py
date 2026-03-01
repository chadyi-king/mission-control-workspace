#!/usr/bin/env python3
"""
Chad Auto-Responder Bridge
Runs on Chad's machine (or Render worker).

Two directions:
  Helios → Chad  : listens on 'chad' channel, prints/handles messages
  Chad → Helios  : parse_telegram_message() converts natural-language text
                   to structured Helios events and publishes them

CLI usage:
  python chad_auto_responder.py "create task audit the dashboard"
  python chad_auto_responder.py              # interactive listener mode
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone

import redis

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
REDIS_URL = os.environ.get("UPSTASH_REDIS_URL", "")
HELIOS_CHANNEL = "helios"
CHAD_CHANNEL = "chad"
NODE_NAME = "chad"


def ts(*parts) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}]", *parts, flush=True)


# --------------------------------------------------------------------------- #
# NLP parser  (Telegram text → Helios structured event)
# --------------------------------------------------------------------------- #

_TASK_CREATE_PATTERNS = [
    r"\bcreate\s+(?:a\s+)?task\b",
    r"\bnew\s+task\b",
    r"\badd\s+task\b",
    r"\btask\s*:\s*",
    r"\bdo\s+(?:this|the following)\b",
]

_TASK_UPDATE_PATTERNS = [
    r"\bupdate\s+task\b",
    r"\bmark\s+(?:task\s+)?(?:as\s+)?(?:done|complete|finished|in.progress|failed)\b",
    r"\btask\s+(?:\w[\w-]*)\s+is\s+(?:done|complete|finished|in.progress|failed)\b",
    r"\b(?:done|finished|completed)\s+(?:with\s+)?task\b",
]

_STATUS_PATTERNS = [
    r"\bstatus\b",
    r"\bhow.s.+going\b",
    r"\bwhat.s\s+(?:up|happening)\b",
    r"\breport\b",
    r"\bshow\s+me\b",
    r"\bupdate\s+me\b",
]

_AGENT_PATTERNS = [
    r"\bspawn\s+agent\b",
    r"\bcreate\s+agent\b",
    r"\bassign\s+(?:this\s+)?to\s+(?:agent\s+)?(\w+)\b",
    r"\bkill\s+agent\b",
    r"\bstop\s+agent\b",
]


def _extract_task_title(text: str) -> str:
    """Strip common command prefixes and return a clean task title."""
    cleaned = re.sub(
        r"(?i)(create\s+(a\s+)?task|new\s+task|add\s+task|task\s*:?\s*)", "", text
    ).strip()
    # Capitalise first letter
    return cleaned[:1].upper() + cleaned[1:] if cleaned else text.strip()


def _extract_task_id(text: str) -> str | None:
    """Try to pull a task-id like 'task-123' or 'TASK-abc' from text."""
    m = re.search(r"\b(task[-_][\w]+)\b", text, re.IGNORECASE)
    return m.group(1) if m else None


def _extract_status(text: str) -> str:
    lower = text.lower()
    for keyword, status in [
        ("in progress", "in_progress"),
        ("in-progress", "in_progress"),
        ("inprogress", "in_progress"),
        ("done", "completed"),
        ("complete", "completed"),
        ("finished", "completed"),
        ("fail", "failed"),
        ("blocked", "blocked"),
        ("pending", "pending"),
    ]:
        if keyword in lower:
            return status
    return "updated"


def parse_telegram_message(text: str) -> dict:
    """
    Convert a natural-language Telegram message into a structured Helios event.

    Returns a dict with keys: type, data
    """
    lower = text.lower()

    # ------------------------------------------------------------------ #
    # status request
    # ------------------------------------------------------------------ #
    if any(re.search(p, lower) for p in _STATUS_PATTERNS):
        return {
            "type": "status_request",
            "data": {"requester": NODE_NAME, "raw": text},
        }

    # ------------------------------------------------------------------ #
    # task update
    # ------------------------------------------------------------------ #
    if any(re.search(p, lower) for p in _TASK_UPDATE_PATTERNS):
        task_id = _extract_task_id(text)
        new_status = _extract_status(text)
        return {
            "type": "task_update",
            "data": {
                "task_id": task_id,
                "status": new_status,
                "raw": text,
            },
        }

    # ------------------------------------------------------------------ #
    # agent command
    # ------------------------------------------------------------------ #
    if any(re.search(p, lower) for p in _AGENT_PATTERNS):
        return {
            "type": "agent_command",
            "data": {"command": text, "raw": text},
        }

    # ------------------------------------------------------------------ #
    # task create (default — if it has imperative content)
    # ------------------------------------------------------------------ #
    if any(re.search(p, lower) for p in _TASK_CREATE_PATTERNS) or len(text.split()) > 3:
        title = _extract_task_title(text)
        return {
            "type": "task_create",
            "data": {
                "title": title,
                "created_by": NODE_NAME,
                "status": "pending",
                "raw": text,
            },
        }

    # ------------------------------------------------------------------ #
    # fallback: generic message
    # ------------------------------------------------------------------ #
    return {
        "type": "message",
        "data": {"text": text, "from": NODE_NAME},
    }


# --------------------------------------------------------------------------- #
# Send to Helios
# --------------------------------------------------------------------------- #

def handle_telegram_input(r: redis.Redis, text: str) -> None:
    """Parse text and publish the resulting event to Helios."""
    event = parse_telegram_message(text)
    payload = {
        "from": NODE_NAME,
        "type": event["type"],
        "data": event["data"],
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    r.publish(HELIOS_CHANNEL, json.dumps(payload))
    ts(f"→ Helios [{event['type']}]:", json.dumps(event["data"])[:120])


# --------------------------------------------------------------------------- #
# Receive from Helios
# --------------------------------------------------------------------------- #

def handle_helios_message(r: redis.Redis, raw: str) -> None:
    """Handle an inbound message from Helios (published on 'chad' channel)."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        ts("Bad JSON from Helios:", raw[:80])
        return

    msg_type = data.get("type", "unknown")
    payload = data.get("data", {})
    ts(f"← Helios [{msg_type}]")

    if msg_type == "task_assigned":
        task = payload.get("task", {})
        ts("Task assigned:", task.get("title", "Untitled"))
        r.publish(HELIOS_CHANNEL, json.dumps({
            "from": NODE_NAME,
            "type": "task_ack",
            "data": {"task_id": task.get("id"), "status": "accepted"},
            "ts": datetime.now(timezone.utc).isoformat(),
        }))

    elif msg_type in ("task_created", "task_updated"):
        task = payload.get("task", {})
        ts(f"  {msg_type}: [{task.get('id', '?')}] {task.get('title', '')} → {task.get('status', '?')}")

    elif msg_type == "status_response":
        ts("  Status:", json.dumps(payload, indent=2))

    elif msg_type == "worker_heartbeat":
        ts("  Worker alive — tasks:", payload.get("tasks", "?"), "agents:", payload.get("agents", "?"))

    elif msg_type == "dashboard_updated":
        ts("  Dashboard data.json updated")

    elif msg_type == "pong":
        ts("  Helios is alive")

    elif msg_type == "alert":
        ts("  ALERT:", payload.get("message", ""))

    else:
        ts(f"  (unhandled type '{msg_type}')")


# --------------------------------------------------------------------------- #
# Main — listener mode
# --------------------------------------------------------------------------- #

def run_listener() -> None:
    if not REDIS_URL:
        raise RuntimeError("UPSTASH_REDIS_URL is not set")

    r = redis.from_url(REDIS_URL, decode_responses=True)
    pub = r.pubsub(ignore_subscribe_messages=True)
    pub.subscribe(CHAD_CHANNEL)
    ts("Listening on channel:", CHAD_CHANNEL)

    for message in pub.listen():
        if message["type"] != "message":
            continue
        handle_helios_message(r, message["data"])


if __name__ == "__main__":
    if not REDIS_URL:
        print("ERROR: UPSTASH_REDIS_URL is not set", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) > 1:
        # CLI: send a message to Helios
        text = " ".join(sys.argv[1:])
        r = redis.from_url(REDIS_URL, decode_responses=True)
        handle_telegram_input(r, text)
    else:
        # No args: run in listener mode
        run_listener()
