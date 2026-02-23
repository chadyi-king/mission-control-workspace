#!/usr/bin/env python3
"""
Helios Background Worker for Render.com
Bridges Redis pub/sub ↔ Helios API REST.

Flow:
  User/Chad  –publishes→  Redis 'helios' or 'chad->helios' channel
  This worker –POSTs→  Helios API  /api/events
  Helios API  –broadcasts→  Dashboard WebSocket

Environment variables required:
  UPSTASH_REDIS_URL     – Upstash Redis URL
  HELIOS_API_URL        – Public URL of the helios-api Render service
                          e.g. https://helios-api-xxxx.onrender.com
"""

import json
import os
import time
import threading
import uuid
from datetime import datetime, timezone

import redis
import requests

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #

def _resolve_redis_url() -> str:
    """
    Build a redis-py-compatible socket URL from whatever env vars are present.
    Priority:
      1. REDIS_URL / UPSTASH_REDIS_URL  (already a redis:// or rediss:// URL)
      2. UPSTASH_REDIS_REST_URL + UPSTASH_REDIS_REST_TOKEN  →  rediss:// TLS URL
    """
    if url := os.environ.get("REDIS_URL"):
        return url
    if url := os.environ.get("UPSTASH_REDIS_URL"):
        return url
    rest_url = os.environ.get("UPSTASH_REDIS_REST_URL", "")
    token = os.environ.get("UPSTASH_REDIS_REST_TOKEN", "")
    if rest_url and token:
        host = rest_url.removeprefix("https://").removeprefix("http://").rstrip("/")
        return f"rediss://default:{token}@{host}:6380"
    return ""


REDIS_URL = _resolve_redis_url()
HELIOS_API_URL = os.environ.get("HELIOS_API_URL", "").rstrip("/")

LISTEN_CHANNELS = ["helios", "chad->helios", "chad"]
SEND_CHANNEL = "chad"

# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def ts(*parts) -> None:
    print(f"[{datetime.now(timezone.utc).isoformat()}]", *parts, flush=True)


def post_to_helios(payload: dict) -> bool:
    """POST a structured event to Helios API /api/events."""
    if not HELIOS_API_URL:
        ts("WARNING: HELIOS_API_URL not set — cannot forward events to API")
        return False
    try:
        resp = requests.post(
            f"{HELIOS_API_URL}/api/events",
            json=payload,
            timeout=10,
        )
        if resp.status_code == 200:
            ts(f"  → Helios API accepted event [{payload.get('event_type','?')}]")
            return True
        else:
            ts(f"  WARNING: Helios API returned {resp.status_code}: {resp.text[:120]}")
            return False
    except requests.RequestException as exc:
        ts("  ERROR posting to Helios API:", exc)
        return False


def redis_msg_to_helios_event(raw_payload: dict) -> dict:
    """
    Convert a Redis pub/sub message (arbitrary shape from Chad / other agents)
    into a Helios API EventIn-compatible payload.
    """
    msg_type = raw_payload.get("type", "generic")
    agent = raw_payload.get("from", raw_payload.get("agent", "worker"))
    data = raw_payload.get("data", raw_payload)

    # Map Redis message types to Helios event_type vocabulary
    type_map = {
        "task_create": "task_create",
        "task_update": "task_update",
        "heartbeat": "heartbeat",
        "status_request": "status_request",
        "agent_update": "agent_update",
        "agent_command": "agent_command",
        "task_ack": "task_ack",
        "message": "message",
    }
    event_type = type_map.get(msg_type, msg_type)

    return {
        "agent": agent,
        "event_type": event_type,
        "status": "success",
        "idempotency_key": raw_payload.get("idempotency_key") or str(uuid.uuid4()),
        "payload": data,
        "model_tier": "fast",
        "ts": raw_payload.get("ts", datetime.now(timezone.utc).isoformat()),
    }


def notify_chad(r: redis.Redis, msg_type: str, data: dict) -> None:
    r.publish(SEND_CHANNEL, json.dumps({
        "from": "helios-worker",
        "type": msg_type,
        "data": data,
        "ts": datetime.now(timezone.utc).isoformat(),
    }))


# --------------------------------------------------------------------------- #
# Event dispatcher
# --------------------------------------------------------------------------- #

def dispatch(r: redis.Redis, raw: str, channel: str) -> None:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        ts("Bad JSON:", exc, "—", raw[:60])
        return

    msg_type = payload.get("type", "unknown")
    ts(f"← [{channel}] type={msg_type}")

    # Skip echo messages that originated from this worker to avoid loops
    if payload.get("from") == "helios-worker":
        return

    # Special case: status_request responds directly via Redis (no Helios event)
    if msg_type == "status_request":
        try:
            resp = requests.get(f"{HELIOS_API_URL}/api/sync", timeout=8)
            summary = resp.json() if resp.ok else {"error": "API unreachable"}
        except Exception:
            summary = {"error": "API unreachable"}
        notify_chad(r, "status_response", summary)
        return

    # Forward all other events to Helios API
    helios_event = redis_msg_to_helios_event(payload)
    post_to_helios(helios_event)


# --------------------------------------------------------------------------- #
# Heartbeat thread
# --------------------------------------------------------------------------- #

def heartbeat_loop(r: redis.Redis) -> None:
    """Send a worker heartbeat every 30 s to keep Helios agent list alive."""
    while True:
        time.sleep(30)
        try:
            post_to_helios({
                "agent": "helios-worker",
                "event_type": "heartbeat",
                "status": "success",
                "idempotency_key": str(uuid.uuid4()),
                "payload": {"status": "active"},
                "model_tier": "fast",
            })
        except Exception as exc:
            ts("Heartbeat error:", exc)


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> None:
    if not REDIS_URL:
        raise RuntimeError("UPSTASH_REDIS_URL is not set")
    if not HELIOS_API_URL:
        ts("WARNING: HELIOS_API_URL not set — status_request will fail; other events will be dropped")

    ts("=" * 60)
    ts("HELIOS BACKGROUND WORKER STARTING")
    ts("  Redis URL :", REDIS_URL[:30], "…")
    ts("  Helios API:", HELIOS_API_URL or "(not set)")
    ts("  Channels  :", LISTEN_CHANNELS)
    ts("=" * 60)

    r: redis.Redis = redis.from_url(REDIS_URL, decode_responses=True)  # type: ignore[assignment]
    pub = r.pubsub(ignore_subscribe_messages=True)
    pub.subscribe(*LISTEN_CHANNELS)

    # Start heartbeat daemon
    hb = threading.Thread(target=heartbeat_loop, args=(r,), daemon=True)
    hb.start()

    # Announce startup via Redis so Chad bot hears it
    notify_chad(r, "worker_started", {"channels": LISTEN_CHANNELS, "helios_api": HELIOS_API_URL})

    ts("Listening…")
    for message in pub.listen():
        if message["type"] != "message":
            continue
        dispatch(r, message["data"], message["channel"])


if __name__ == "__main__":
    main()
