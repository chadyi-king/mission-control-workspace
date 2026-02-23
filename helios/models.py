from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EventStatus(str, Enum):
    success = "success"
    failure = "failure"
    partial = "partial"


class ModelTier(str, Enum):
    cheap = "cheap"
    mid = "mid"
    best = "best"


class EventIn(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    agent: str
    ts: datetime
    event_type: str
    payload: dict[str, Any]
    status: EventStatus
    idempotency_key: str
    model_tier: ModelTier
    model_id: str
    reasoning_summary: str
    confidence: float = Field(ge=0.0, le=1.0)


class HeartbeatIn(BaseModel):
    agent: str
    ts: datetime


class AgentOut(BaseModel):
    agent: str
    last_seen: datetime
    status: str
