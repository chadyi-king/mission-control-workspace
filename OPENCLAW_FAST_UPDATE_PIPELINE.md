# OpenClaw Fast Update Pipeline (Telegram/Chad → Helios → Dashboard)

This adds a fast runtime bridge so Chad/Telegram bus messages can flow into Helios events and trigger near-real-time dashboard refresh behavior.

## Data flow

1. Chad/Telegram side publishes task-like JSON messages to Redis channels (legacy + arrow conventions supported).
2. `chad_helios_event_bridge.py` subscribes to Redis channels and transforms each message into Helios `EventIn` payload shape.
3. Bridge posts transformed events to `POST /api/events` and sends periodic heartbeats to `POST /api/heartbeat`.
4. Helios emits websocket notifications on `/ws/dashboard` (`event`, `heartbeat`, plus snapshot).
5. Dashboard listens on websocket and triggers immediate refresh (existing load/render path), with polling kept as fallback.

## Runtime paths

- Bridge script: `/home/chad-yi/.openclaw/workspace/chad_helios_event_bridge.py`
- Helios API: `/home/chad-yi/mission-control-workspace/helios/service.py`
- Dashboard UI: `/home/chad-yi/.openclaw/workspace/mission-control-dashboard/index.html`

## Required env vars

- `HELIOS_API_BASE` (default: `http://localhost:8000`)
- `REDIS_URL` or `UPSTASH_REDIS_URL` (default fallback: `redis://localhost:6379/0`)
- `BRIDGE_AGENT_NAME` (default: `chad`)
- `BRIDGE_REDIS_CHANNELS` (optional CSV; defaults include `helios` and `chad→helios` variants)
- `BRIDGE_HEARTBEAT_INTERVAL` (seconds, default `30`)

## Run

1. Start Helios API (FastAPI/uvicorn as used in your environment).
2. Start bridge:
   - `python /home/chad-yi/.openclaw/workspace/chad_helios_event_bridge.py`
3. Open dashboard and ensure websocket points to Helios (`ws://.../ws/dashboard`).

## Manual smoke checks

- Bridge logs should show:
  - Redis connection + subscribed channels
  - heartbeat success
  - event forward success with idempotency key
- `GET /api/sync` should return updated summary after Redis messages.
- Dashboard should refresh quickly on websocket `event`/`heartbeat`, while polling still works if websocket is unavailable.
