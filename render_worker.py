#!/usr/bin/env python3
"""
Helios Background Worker for Render.com
Listens to Redis, manages task/agent state, writes data.json for the dashboard.
No internal module dependencies — only the redis package is required.
"""

import json
import os
import threading
import time
from datetime import datetime, timezone

import redis

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
REDIS_URL = os.environ.get("UPSTASH_REDIS_URL", "")
DATA_JSON_PATH = os.environ.get("DATA_JSON_PATH", "/tmp/data.json")

LISTEN_CHANNELS = ["helios", "chad->helios"]
SEND_CHANNEL = "chad"

# --------------------------------------------------------------------------- #
# State (in-memory; refreshed from data.json on startup if it exists)
# --------------------------------------------------------------------------- #
state: dict = {
    "agents": {},
    "tasks": {},
    "system": {
        "status": "initialising",
        "worker_started": datetime.now(timezone.utc).isoformat(),
    },
    "lastUpdated": datetime.now(timezone.utc).isoformat(),
}


def load_state_from_disk() -> None:
    """Seed in-memory state from an existing data.json, if present."""
    global state
    try:
        with open(DATA_JSON_PATH) as fh:
            on_disk = json.load(fh)
        state.update(on_disk)
        ts("Seeded state from", DATA_JSON_PATH)
    except FileNotFoundError:
        ts("No existing data.json found — starting fresh")
    except Exception as exc:
        ts("Warning: could not read data.json:", exc)


def ts(*parts) -> None:
    """Timestamped print, always flushed."""
    print(f"[{datetime.now(timezone.utc).isoformat()}]", *parts, flush=True)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def write_data_json() -> None:
    """Persist current state to data.json for the dashboard."""
    state["lastUpdated"] = datetime.now(timezone.utc).isoformat()
    tmp = DATA_JSON_PATH + ".tmp"
    try:
        with open(tmp, "w") as fh:
            json.dump(state, fh, indent=2)
        os.replace(tmp, DATA_JSON_PATH)
        ts("data.json written →", DATA_JSON_PATH)
    except Exception as exc:
        ts("ERROR writing data.json:", exc)


def publish(r: redis.Redis, channel: str, payload: dict) -> None:
    r.publish(channel, json.dumps(payload))


def notify_chad(r: redis.Redis, msg_type: str, data: dict) -> None:
    publish(r, SEND_CHANNEL, {
        "from": "helios-worker",
        "type": msg_type,
        "data": data,
        "ts": datetime.now(timezone.utc).isoformat(),
    })


# --------------------------------------------------------------------------- #
# Event handlers
# --------------------------------------------------------------------------- #

def handle_heartbeat(r: redis.Redis, payload: dict) -> None:
    agent_id = payload.get("agent_id") or payload.get("from", "unknown")
    state["agents"].setdefault(agent_id, {})
    state["agents"][agent_id].update({
        "last_seen": payload.get("ts", datetime.now(timezone.utc).isoformat()),
        "status": payload.get("status", "active"),
    })
    write_data_json()


def handle_task_create(r: redis.Redis, payload: dict) -> None:
    task = payload.get("data", payload)
    task_id = task.get("id") or f"task-{int(time.time())}"
    state["tasks"][task_id] = {
        **task,
        "id": task_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": task.get("status", "pending"),
    }
    ts("Task created:", task_id)
    write_data_json()
    notify_chad(r, "task_created", {"task_id": task_id, "task": state["tasks"][task_id]})


def handle_task_update(r: redis.Redis, payload: dict) -> None:
    data = payload.get("data", payload)
    task_id = data.get("task_id") or data.get("id")
    if not task_id:
        ts("task_update missing task_id — skipping")
        return
    state["tasks"].setdefault(task_id, {})
    state["tasks"][task_id].update(data)
    state["tasks"][task_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
    ts("Task updated:", task_id, "→", data.get("status", "?"))
    write_data_json()
    notify_chad(r, "task_updated", {"task_id": task_id, "task": state["tasks"][task_id]})


def handle_status_request(r: redis.Redis, payload: dict) -> None:
    ts("Status request received")
    summary = {
        "agents": len(state["agents"]),
        "tasks": {
            "total": len(state["tasks"]),
            "pending": sum(1 for t in state["tasks"].values() if t.get("status") == "pending"),
            "in_progress": sum(1 for t in state["tasks"].values() if t.get("status") == "in_progress"),
            "completed": sum(1 for t in state["tasks"].values() if t.get("status") == "completed"),
        },
        "system": state["system"],
        "lastUpdated": state["lastUpdated"],
    }
    notify_chad(r, "status_response", summary)


def handle_agent_update(r: redis.Redis, payload: dict) -> None:
    data = payload.get("data", payload)
    agent_id = data.get("agent_id") or data.get("id") or payload.get("from", "unknown")
    state["agents"].setdefault(agent_id, {})
    state["agents"][agent_id].update({**data, "updated_at": datetime.now(timezone.utc).isoformat()})
    ts("Agent updated:", agent_id)
    write_data_json()


HANDLERS = {
    "heartbeat": handle_heartbeat,
    "task_create": handle_task_create,
    "task_update": handle_task_update,
    "status_request": handle_status_request,
    "agent_update": handle_agent_update,
}


def dispatch(r: redis.Redis, raw: str) -> None:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        ts("Bad JSON:", exc)
        return

    msg_type = payload.get("type", "unknown")
    ts("← event:", msg_type)

    handler = HANDLERS.get(msg_type)
    if handler:
        try:
            handler(r, payload)
        except Exception as exc:
            ts("ERROR in handler", msg_type, ":", exc)
    else:
        ts("No handler for event type:", msg_type)


# --------------------------------------------------------------------------- #
# Heartbeat thread
# --------------------------------------------------------------------------- #

def heartbeat_loop(r: redis.Redis) -> None:
    while True:
        time.sleep(30)
        try:
            state["system"]["status"] = "active"
            state["system"]["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
            write_data_json()
            notify_chad(r, "worker_heartbeat", {
                "status": "active",
                "tasks": len(state["tasks"]),
                "agents": len(state["agents"]),
            })
        except Exception as exc:
            ts("Heartbeat error:", exc)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> None:
    if not REDIS_URL:
        raise RuntimeError("UPSTASH_REDIS_URL is not set")

    ts("=" * 60)
    ts("HELIOS BACKGROUND WORKER STARTING")
    ts("  Redis URL:", REDIS_URL[:30], "…")
    ts("  data.json path:", DATA_JSON_PATH)
    ts("  Channels:", LISTEN_CHANNELS)
    ts("=" * 60)

    load_state_from_disk()
    state["system"]["status"] = "active"

    r = redis.from_url(REDIS_URL, decode_responses=True)
    pub = r.pubsub(ignore_subscribe_messages=True)
    pub.subscribe(*LISTEN_CHANNELS)

    # Start heartbeat thread
    hb = threading.Thread(target=heartbeat_loop, args=(r,), daemon=True)
    hb.start()

    # Announce startup
    notify_chad(r, "worker_started", {"channels": LISTEN_CHANNELS})
    write_data_json()

    ts("Listening…")
    for message in pub.listen():
        if message["type"] != "message":
            continue
        dispatch(r, message["data"])


if __name__ == "__main__":
    main()
