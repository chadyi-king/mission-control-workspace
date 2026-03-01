from collections import deque
from datetime import datetime, timezone
from threading import Lock
from typing import Any
from uuid import uuid4

from helios.adapters import ExternalAdapters
from helios.models import EventIn


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class InMemoryStore:
    def __init__(self, adapters: ExternalAdapters | None = None) -> None:
        self.lock = Lock()
        self.adapters = adapters
        self.metrics = {
            "events_ingested": 0,
            "events_failed": 0,
            "queue_length": 0,
            "db_errors": 0,
        }
        self.idempotency_keys: set[str] = set()
        self.events: list[dict[str, Any]] = []
        self.queue: deque[dict[str, Any]] = deque()
        self.agents: dict[str, datetime] = {
            "chad": utcnow(),
            "cerebronn": utcnow(),
            "helios": utcnow(),
        }
        self.last_audit = utcnow()

    def update_heartbeat(self, agent: str, timestamp: datetime) -> None:
        with self.lock:
            self.agents[agent] = timestamp

    def ingest_event(self, event: EventIn) -> tuple[bool, dict[str, Any]]:
        with self.lock:
            if event.idempotency_key in self.idempotency_keys:
                return False, {"accepted": False, "reason": "duplicate"}

            event_id = str(uuid4())
            record = {
                "event_id": event_id,
                "agent": event.agent,
                "ts": event.ts.isoformat(),
                "event_type": event.event_type,
                "status": event.status.value,
                "idempotency_key": event.idempotency_key,
                "payload": event.payload,
                "model_tier": event.model_tier.value,
                "model_id": event.model_id,
                "reasoning_summary": event.reasoning_summary,
                "confidence": event.confidence,
            }
            self.idempotency_keys.add(event.idempotency_key)
            self.events.append(record)
            self.queue.append(record)
            self.metrics["events_ingested"] += 1
            self.metrics["queue_length"] = len(self.queue)
            self.last_audit = utcnow()
            self.agents[event.agent] = event.ts

            if self.adapters is not None:
                try:
                    self.adapters.publish_event(record)
                    self.adapters.persist_event(record)
                except Exception:
                    self.metrics["db_errors"] += 1

            return True, {"accepted": True, "event_id": event_id}

    def replay(self, count: int) -> int:
        with self.lock:
            replay_count = min(count, len(self.events))
            for item in self.events[-replay_count:]:
                self.queue.append(item)
            self.metrics["queue_length"] = len(self.queue)
            self.last_audit = utcnow()
            return replay_count

    def summary(self) -> dict[str, Any]:
        with self.lock:
            recent_events = self.events[-20:]
            agents = []
            now = utcnow()
            for name, seen in self.agents.items():
                delta_seconds = (now - seen).total_seconds()
                if delta_seconds <= 90:
                    status = "online"
                elif delta_seconds <= 900:
                    status = "idle"
                else:
                    status = "offline"
                agents.append(
                    {
                        "agent": name,
                        "last_seen": seen.isoformat(),
                        "status": status,
                    }
                )
            return {
                "agents": agents,
                "recent_events": recent_events,
                "metrics": self.metrics,
                "last_audit": self.last_audit.isoformat(),
            }
