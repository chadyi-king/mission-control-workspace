import json
from datetime import datetime, timezone
from typing import Dict, Iterable, List, Optional, Tuple

from redis import Redis


class RedisBackbone:
    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url, decode_responses=True)

    def ensure_group(self, stream: str, group: str) -> None:
        try:
            self.redis.xgroup_create(stream, group, id="0", mkstream=True)
        except Exception as exc:
            if "BUSYGROUP" not in str(exc):
                raise

    def publish_stream(self, stream: str, payload: Dict) -> str:
        data = {k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) for k, v in payload.items()}
        return self.redis.xadd(stream, data)

    def read_group(self, stream: str, group: str, consumer: str, block_ms: int = 5000, count: int = 10):
        return self.redis.xreadgroup(group, consumer, {stream: ">"}, count=count, block=block_ms)

    def claim_stale(self, stream: str, group: str, consumer: str, min_idle_ms: int, count: int = 20):
        next_cursor = "0-0"
        reclaimed = []
        while True:
            next_cursor, messages, _ = self.redis.xautoclaim(
                stream,
                group,
                consumer,
                min_idle_ms=min_idle_ms,
                start_id=next_cursor,
                count=count,
            )
            reclaimed.extend(messages)
            if next_cursor == "0-0" or not messages:
                break
        return reclaimed

    def ack(self, stream: str, group: str, message_id: str) -> int:
        return self.redis.xack(stream, group, message_id)

    def add_processed_signal(self, signal_id: str) -> bool:
        return self.redis.sadd("quanta.processed_signals", signal_id) == 1

    def is_processed_signal(self, signal_id: str) -> bool:
        return self.redis.sismember("quanta.processed_signals", signal_id)

    def set_last_telegram_id(self, message_id: int) -> None:
        self.redis.set("quanta.telegram.last_message_id", message_id)

    def get_last_telegram_id(self) -> int:
        value = self.redis.get("quanta.telegram.last_message_id")
        return int(value) if value else 0

    def save_signal_patterns(self, payload: Dict) -> None:
        self.redis.set("quanta.signal_patterns", json.dumps(payload))

    def load_signal_patterns(self) -> Dict:
        value = self.redis.get("quanta.signal_patterns")
        return json.loads(value) if value else {}

    def save_trade_state(self, trade_id: str, payload: Dict) -> None:
        key = f"quanta.trade.state:{trade_id}"
        data = {k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) for k, v in payload.items()}
        self.redis.hset(key, mapping=data)

    def load_trade_state(self, trade_id: str) -> Dict:
        key = f"quanta.trade.state:{trade_id}"
        out = {}
        for k, v in self.redis.hgetall(key).items():
            if isinstance(v, str) and (v.startswith("{") or v.startswith("[")):
                out[k] = json.loads(v)
            elif v in {"True", "False"}:
                out[k] = v == "True"
            else:
                try:
                    out[k] = float(v) if "." in v else int(v)
                except Exception:
                    out[k] = v
        return out

    def increment_trade_count(self) -> int:
        return self.redis.incr("quanta.risk.trade_count")

    def get_trade_count(self) -> int:
        value = self.redis.get("quanta.risk.trade_count")
        return int(value) if value else 0

    def set_baseline_equity(self, equity: float) -> None:
        self.redis.set("quanta.risk.baseline_equity", equity)

    def get_baseline_equity(self) -> Optional[float]:
        value = self.redis.get("quanta.risk.baseline_equity")
        return float(value) if value else None

    def set_risk_mode(self, mode: str) -> None:
        self.redis.set("quanta.risk.mode", mode)

    def get_risk_mode(self) -> str:
        return self.redis.get("quanta.risk.mode") or "fixed_20"


def event_payload(event_type: str, data: Dict) -> Dict:
    return {
        "from": "quanta-v3",
        "type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }
