#!/usr/bin/env python3
"""Redis -> Helios Event bridge for fast Mission Control dashboard updates.

Listens on Chad/Helios Redis pubsub channels and forwards messages to Helios
`/api/events`, while sending periodic `/api/heartbeat` pings.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import signal
import threading
import time
from datetime import datetime, timezone
from typing import Any, cast

import requests
from redis import Redis
from redis.exceptions import RedisError
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


DEFAULT_CHANNELS = [
    "helios",
    "chad→helios",
    "chad->helios",
    "chad_to_helios",
    "chad:helios",
]


def setup_logging() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def to_iso_utc(value: Any) -> str:
    if isinstance(value, datetime):
        dt = value
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()

    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat()

    if isinstance(value, str) and value.strip():
        raw = value.strip()
        try:
            if raw.endswith("Z"):
                raw = raw[:-1] + "+00:00"
            dt = datetime.fromisoformat(raw)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc).isoformat()
        except ValueError:
            pass

    return now_iso()


def clamp_confidence(value: Any) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return 0.5
    return max(0.0, min(1.0, v))


def normalize_status(value: Any) -> str:
    status = str(value or "").strip().lower()
    if status in {"success", "ok", "done", "completed", "accepted"}:
        return "success"
    if status in {"failure", "failed", "error", "rejected"}:
        return "failure"
    if status in {"partial", "in_progress", "processing"}:
        return "partial"
    return "success"


def normalize_model_tier(value: Any) -> str:
    tier = str(value or "").strip().lower()
    if tier in {"cheap", "mid", "best"}:
        return tier
    return "cheap"


def parse_channels(raw: str | None) -> list[str]:
    if not raw:
        return DEFAULT_CHANNELS
    parsed = [c.strip() for c in raw.split(",") if c.strip()]
    return parsed or DEFAULT_CHANNELS


def short_json(value: Any, limit: int = 220) -> str:
    try:
        text = json.dumps(value, ensure_ascii=False)
    except Exception:
        text = str(value)
    if len(text) > limit:
        return text[: limit - 1] + "…"
    return text


class ChadHeliosEventBridge:
    def __init__(self) -> None:
        self.agent_name = os.getenv("BRIDGE_AGENT_NAME", "chad").strip() or "chad"
        self.helios_api_base = os.getenv("HELIOS_API_BASE", "http://localhost:8000").rstrip("/")
        self.redis_url = os.getenv("REDIS_URL") or os.getenv("UPSTASH_REDIS_URL") or "redis://localhost:6379/0"
        self.channels = parse_channels(os.getenv("BRIDGE_REDIS_CHANNELS"))
        self.heartbeat_interval = max(5, int(os.getenv("BRIDGE_HEARTBEAT_INTERVAL", "30")))
        self.request_timeout = max(2.0, float(os.getenv("BRIDGE_REQUEST_TIMEOUT", "8")))

        self.stop_event = threading.Event()
        self.session = self._build_session()
        self.redis: Redis = cast(Redis, Redis.from_url(self.redis_url, decode_responses=True))

    @staticmethod
    def _build_session() -> requests.Session:
        session = requests.Session()
        retry = Retry(
            total=3,
            connect=3,
            read=3,
            backoff_factor=0.4,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=frozenset({"GET", "POST"}),
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any] | None:
        url = f"{self.helios_api_base}{path}"
        try:
            res = self.session.post(url, json=payload, timeout=self.request_timeout)
            body = res.json() if "application/json" in res.headers.get("content-type", "") else {"raw": res.text}
            if res.ok:
                return body
            logging.warning("POST %s failed status=%s body=%s", path, res.status_code, short_json(body))
            return None
        except Exception as exc:
            logging.error("POST %s error: %s", path, exc)
            return None

    def _heartbeat_loop(self) -> None:
        logging.info("Heartbeat loop started interval=%ss", self.heartbeat_interval)
        while not self.stop_event.is_set():
            payload = {
                "agent": self.agent_name,
                "ts": now_iso(),
            }
            result = self._post_json("/api/heartbeat", payload)
            if result is not None:
                logging.debug("Heartbeat ok: %s", short_json(result))
            self.stop_event.wait(self.heartbeat_interval)
        logging.info("Heartbeat loop stopped")

    def _build_event_payload(self, channel: str, message_data: Any) -> dict[str, Any]:
        event: dict[str, Any] = message_data if isinstance(message_data, dict) else {"raw": message_data}
        nested_payload_raw = event.get("data")
        nested_payload: dict[str, Any] = nested_payload_raw if isinstance(nested_payload_raw, dict) else {}

        source_agent = (
            event.get("from")
            or event.get("agent")
            or event.get("source")
            or nested_payload.get("from")
            or self.agent_name
        )
        event_type = (
            event.get("type")
            or event.get("event_type")
            or nested_payload.get("type")
            or "redis_message"
        )

        ts_value = (
            event.get("timestamp")
            or event.get("ts")
            or nested_payload.get("timestamp")
            or nested_payload.get("ts")
        )
        ts = to_iso_utc(ts_value)

        identity_seed = (
            event.get("id")
            or event.get("event_id")
            or event.get("idempotency_key")
            or f"{channel}:{event_type}:{source_agent}:{short_json(event)}"
        )
        idempotency_key = hashlib.sha1(str(identity_seed).encode("utf-8")).hexdigest()

        payload = {
            "agent": str(source_agent),
            "ts": ts,
            "event_type": str(event_type),
            "payload": {
                "bridge": "openclaw-redis-bridge",
                "channel": channel,
                "raw": event,
            },
            "status": normalize_status(event.get("status") or nested_payload.get("status")),
            "idempotency_key": idempotency_key,
            "model_tier": normalize_model_tier(event.get("model_tier") or nested_payload.get("model_tier")),
            "model_id": str(event.get("model_id") or nested_payload.get("model_id") or "redis-bridge"),
            "reasoning_summary": str(
                event.get("reasoning_summary")
                or nested_payload.get("reasoning_summary")
                or f"Bridged Redis {event_type} from channel '{channel}'"
            ),
            "confidence": clamp_confidence(event.get("confidence") or nested_payload.get("confidence")),
        }
        return payload

    def _event_loop(self) -> None:
        logging.info("Connecting to Redis and subscribing channels=%s", self.channels)
        pubsub = self.redis.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe(*self.channels)

        logging.info("Bridge live: redis->helios channel listener started")
        try:
            for message in pubsub.listen():
                if self.stop_event.is_set():
                    break
                if message.get("type") != "message":
                    continue

                channel = str(message.get("channel", "unknown"))
                raw_data = message.get("data")

                try:
                    decoded = json.loads(raw_data) if isinstance(raw_data, str) else raw_data
                except json.JSONDecodeError:
                    decoded = {"raw": raw_data}

                event_payload = self._build_event_payload(channel=channel, message_data=decoded)
                logging.info(
                    "Redis message channel=%s event_type=%s agent=%s",
                    channel,
                    event_payload.get("event_type"),
                    event_payload.get("agent"),
                )
                result = self._post_json("/api/events", event_payload)
                if result is not None:
                    logging.info("Forwarded to /api/events ok idempotency=%s", event_payload.get("idempotency_key"))
        except RedisError as exc:
            logging.error("Redis listener error: %s", exc)
        finally:
            pubsub.close()
            logging.info("Redis listener stopped")

    def _check_connectivity(self) -> None:
        self.redis.ping()
        health = self.session.get(f"{self.helios_api_base}/api/health", timeout=self.request_timeout)
        health.raise_for_status()
        logging.info("Connectivity ok: redis + Helios (%s)", self.helios_api_base)

    def run(self) -> None:
        self._check_connectivity()

        hb_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        hb_thread.start()

        self._event_loop()

    def stop(self) -> None:
        self.stop_event.set()


def main() -> int:
    setup_logging()
    bridge = ChadHeliosEventBridge()

    def _handle_signal(signum: int, _frame: Any) -> None:
        logging.info("Received signal=%s, shutting down bridge...", signum)
        bridge.stop()

    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    try:
        bridge.run()
        return 0
    except Exception as exc:
        logging.exception("Bridge failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
