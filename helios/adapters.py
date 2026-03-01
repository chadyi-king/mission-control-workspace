from typing import Any
import json

import requests

from helios.config import HeliosConfig

try:
    import redis
except Exception:  # pragma: no cover
    redis = None

try:
    import psycopg
except Exception:  # pragma: no cover
    psycopg = None


class ExternalAdapters:
    def __init__(self, config: HeliosConfig) -> None:
        self.config = config
        self.redis_client = None
        if redis and config.redis_url:
            try:
                self.redis_client = redis.from_url(config.redis_url, decode_responses=True)
            except Exception as exc:
                print(f"[helios] Redis client init failed (non-fatal): {exc}", flush=True)
                self.redis_client = None

    def publish_event(self, event: dict[str, Any]) -> None:
        if self.redis_client is None:
            return
        self.redis_client.xadd("helios.events", event)

    def persist_event(self, event: dict[str, Any]) -> None:
        if not self.config.postgres_dsn or psycopg is None:
            return

        with psycopg.connect(self.config.postgres_dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS helios_events (
                      event_id TEXT PRIMARY KEY,
                      agent TEXT NOT NULL,
                      ts TEXT NOT NULL,
                      event_type TEXT NOT NULL,
                      status TEXT NOT NULL,
                      idempotency_key TEXT NOT NULL UNIQUE,
                      payload JSONB,
                      model_tier TEXT,
                      model_id TEXT,
                      reasoning_summary TEXT,
                      confidence DOUBLE PRECISION
                    )
                    """
                )
                cur.execute(
                    """
                    INSERT INTO helios_events
                    (event_id, agent, ts, event_type, status, idempotency_key, payload, model_tier, model_id, reasoning_summary, confidence)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s, %s)
                    ON CONFLICT (idempotency_key) DO NOTHING
                    """,
                    (
                        event["event_id"],
                        event["agent"],
                        event["ts"],
                        event["event_type"],
                        event["status"],
                        event["idempotency_key"],
                        json.dumps(event.get("payload", {})),
                        event.get("model_tier"),
                        event.get("model_id"),
                        event.get("reasoning_summary"),
                        event.get("confidence"),
                    ),
                )
            conn.commit()

    def notify_chad(self, text: str) -> None:
        if not self.config.emit_notifications:
            return

        if self.config.discord_webhook_url:
            requests.post(self.config.discord_webhook_url, json={"content": text}, timeout=5)

        if self.config.telegram_bot_token and self.config.telegram_chat_id:
            requests.post(
                f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage",
                json={"chat_id": self.config.telegram_chat_id, "text": text},
                timeout=5,
            )
