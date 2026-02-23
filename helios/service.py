import asyncio
import json
import os
import threading
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from helios.adapters import ExternalAdapters
from helios.config import load_config
from helios.models import AgentOut, EventIn, EventStatus, HeartbeatIn, ModelTier
from helios.store import InMemoryStore

config = load_config()
adapters = ExternalAdapters(config)
store = InMemoryStore(adapters=adapters)

PROTECTED_FILES = {"AGENTS.md", "SOUL.md"}

_loop: asyncio.AbstractEventLoop | None = None


# --------------------------------------------------------------------------- #
# Dashboard WebSocket hub
# --------------------------------------------------------------------------- #


class DashboardHub:
    def __init__(self) -> None:
        self.connections: set[WebSocket] = set()

    async def connect(self, socket: WebSocket) -> None:
        await socket.accept()
        self.connections.add(socket)

    def disconnect(self, socket: WebSocket) -> None:
        self.connections.discard(socket)

    async def broadcast(self, payload: dict[str, Any]) -> None:
        dropped: list[WebSocket] = []
        for connection in self.connections:
            try:
                await connection.send_json(payload)
            except Exception:
                dropped.append(connection)
        for dead in dropped:
            self.disconnect(dead)


hub = DashboardHub()


# --------------------------------------------------------------------------- #
# Redis pub/sub listener (background thread → ingest into store + broadcast)
# --------------------------------------------------------------------------- #


def _redis_listener() -> None:
    """Subscribe to Redis channels and forward events into the in-memory store."""
    import os

    # Resolve Redis URL — support REST creds (Upstash) as well as direct socket URLs
    rest_url = os.getenv("UPSTASH_REDIS_REST_URL", "")
    token = os.getenv("UPSTASH_REDIS_REST_TOKEN", "")
    upstash_socket = (
        "rediss://default:{}@{}:6379".format(
            token,
            rest_url.removeprefix("https://").removeprefix("http://").rstrip("/"),
        )
        if rest_url and token
        else ""
    )
    redis_url = (
        config.redis_url
        or os.getenv("UPSTASH_REDIS_URL")
        or upstash_socket
    )
    if not redis_url:
        print("[helios] No Redis URL configured — Redis subscriber disabled", flush=True)
        return

    try:
        import redis as redis_lib

        r: redis_lib.Redis = redis_lib.from_url(redis_url, decode_responses=True)  # type: ignore[assignment]
        pub = r.pubsub(ignore_subscribe_messages=True)
        pub.subscribe("helios", "chad->helios")
    except Exception as exc:
        print(f"[helios] Redis subscriber failed to start: {exc}", flush=True)
        return

    print("[helios] Redis subscriber started on: helios, chad->helios", flush=True)

    for message in pub.listen():
        if message["type"] != "message":
            continue
        try:
            raw = json.loads(message["data"])
        except json.JSONDecodeError:
            continue

        msg_type = str(raw.get("type", "message"))
        agent = str(raw.get("from", raw.get("agent", "external")))
        data_payload = raw.get("data", raw)
        if not isinstance(data_payload, dict):
            data_payload = {"raw": str(data_payload)}

        event = EventIn(
            agent=agent,
            ts=datetime.now(timezone.utc),
            event_type=msg_type,
            status=EventStatus.success,
            idempotency_key=str(raw.get("idempotency_key") or uuid.uuid4()),
            payload=data_payload,
            model_tier=ModelTier.cheap,
            model_id="redis-bridge",
            reasoning_summary="",
            confidence=1.0,
        )
        accepted, result = store.ingest_event(event)

        if accepted and _loop is not None and not _loop.is_closed():
            asyncio.run_coroutine_threadsafe(
                hub.broadcast(
                    {
                        "type": "event",
                        "accepted": True,
                        "agent": agent,
                        "event_type": msg_type,
                        "result": result,
                    }
                ),
                _loop,
            )


# --------------------------------------------------------------------------- #
# App lifespan — start Redis subscriber on boot
# --------------------------------------------------------------------------- #


@asynccontextmanager
async def _lifespan(application: FastAPI):  # type: ignore[type-arg]
    global _loop
    _loop = asyncio.get_event_loop()
    t = threading.Thread(target=_redis_listener, daemon=True, name="redis-sub")
    t.start()
    yield


app = FastAPI(title="Helios Service", version="0.1.0", lifespan=_lifespan)

# CORS — allow dashboard origin to call API
_allowed_origins = os.getenv(
    "CORS_ALLOWED_ORIGINS",
    "https://mission-control-dashboard-hf0r.onrender.com",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _is_protected_write(payload: dict[str, Any]) -> bool:
    target = str(payload.get("target_file", ""))
    action = str(payload.get("action", ""))
    if not target:
        return False
    hit = any(target.endswith(name) for name in PROTECTED_FILES)
    return hit and action in {"write", "modify", "delete", "replace"}


# --------------------------------------------------------------------------- #
# REST endpoints
# --------------------------------------------------------------------------- #


@app.get("/api/health")
def get_health() -> dict[str, Any]:
    snapshot = store.summary()
    return {
        "status": "ok",
        "agents_count": len(snapshot["agents"]),
        "last_audit": snapshot["last_audit"],
        "metrics": snapshot["metrics"],
    }


@app.get("/api/agents", response_model=list[AgentOut])
def get_agents() -> list[AgentOut]:
    snapshot = store.summary()
    return [AgentOut(**a) for a in snapshot["agents"]]


@app.post("/api/heartbeat")
async def post_heartbeat(heartbeat: HeartbeatIn) -> dict[str, Any]:
    store.update_heartbeat(heartbeat.agent, heartbeat.ts)
    await hub.broadcast(
        {
            "type": "heartbeat",
            "agent": heartbeat.agent,
            "ts": heartbeat.ts.isoformat(),
        }
    )
    return {"ok": True, "agent": heartbeat.agent, "ts": heartbeat.ts.isoformat()}


@app.post("/api/events")
async def post_events(event: EventIn) -> dict[str, Any]:
    if _is_protected_write(event.payload):
        raise HTTPException(status_code=403, detail="Protected governance file modification blocked")

    accepted, result = store.ingest_event(event)
    await hub.broadcast(
        {
            "type": "event",
            "accepted": accepted,
            "result": result,
            "agent": event.agent,
            "event_type": event.event_type,
            "status": event.status.value,
            "idempotency_key": event.idempotency_key,
        }
    )
    if accepted:
        adapters.notify_chad(f"Helios: event accepted from {event.agent} ({event.event_type})")
    return result


@app.post("/api/replay")
def post_replay(
    count: int = Query(default=10, ge=1, le=500),
    x_helios_replay_token: str | None = Header(default=None),
) -> dict[str, Any]:
    if x_helios_replay_token != config.replay_token:
        raise HTTPException(status_code=401, detail="Invalid replay token")
    replayed = store.replay(count)
    return {"replayed": replayed}


@app.get("/api/sync")
def get_sync() -> dict[str, Any]:
    return store.summary()


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "helios", "status": "running", "ts": datetime.now(timezone.utc).isoformat()}


# --------------------------------------------------------------------------- #
# WebSocket
# --------------------------------------------------------------------------- #


@app.websocket("/ws/dashboard")
async def dashboard_ws(websocket: WebSocket) -> None:
    await hub.connect(websocket)
    await websocket.send_json({"type": "snapshot", "data": store.summary()})
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        hub.disconnect(websocket)
