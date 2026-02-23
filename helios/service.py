from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Query, WebSocket, WebSocketDisconnect

from helios.adapters import ExternalAdapters
from helios.config import load_config
from helios.models import AgentOut, EventIn, HeartbeatIn
from helios.store import InMemoryStore

app = FastAPI(title="Helios Service", version="0.1.0")
config = load_config()
adapters = ExternalAdapters(config)
store = InMemoryStore(adapters=adapters)

PROTECTED_FILES = {"AGENTS.md", "SOUL.md"}


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


def _is_protected_write(payload: dict[str, Any]) -> bool:
    target = str(payload.get("target_file", ""))
    action = str(payload.get("action", ""))
    if not target:
        return False
    hit = any(target.endswith(name) for name in PROTECTED_FILES)
    return hit and action in {"write", "modify", "delete", "replace"}


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
    if accepted:
        return result
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


@app.websocket("/ws/dashboard")
async def dashboard_ws(websocket: WebSocket) -> None:
    await hub.connect(websocket)
    await websocket.send_json({"type": "snapshot", "data": store.summary()})
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        hub.disconnect(websocket)
