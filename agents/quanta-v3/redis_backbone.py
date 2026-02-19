import json
import time
from typing import Any, Dict, List, Optional

from redis import Redis


class RedisState:
    def __init__(self, redis_url: str):
        self.redis = Redis.from_url(redis_url, decode_responses=True)

    def get_telegram_state(self) -> Dict[str, Any]:
        try:
            raw = self.redis.get("quanta.telegram.state")
            if not raw:
                return {"channel_id": None, "last_processed_message_id": 0}
            return json.loads(raw)
        except Exception:
            return {"channel_id": None, "last_processed_message_id": 0}

    def set_telegram_state(self, state: Dict[str, Any]) -> None:
        try:
            self.redis.set("quanta.telegram.state", json.dumps(state))
        except Exception:
            raise

    def is_processed_signal(self, signal_id: str) -> bool:
        try:
            return bool(self.redis.sismember("quanta.processed_signals", signal_id))
        except Exception:
            return False

    def mark_processed_signal(self, signal_id: str) -> None:
        try:
            self.redis.sadd("quanta.processed_signals", signal_id)
        except Exception:
            raise

    def save_signal_state(self, signal_id: str, state: Dict[str, Any]) -> None:
        try:
            payload = {k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) for k, v in state.items()}
            self.redis.hset(f"quanta.signal:{signal_id}", mapping=payload)
            self.redis.sadd("quanta.active_signals", signal_id)
        except Exception:
            raise

    def load_signal_state(self, signal_id: str) -> Dict[str, Any]:
        try:
            raw = self.redis.hgetall(f"quanta.signal:{signal_id}")
            state: Dict[str, Any] = {}
            for k, v in raw.items():
                if v.startswith("[") or v.startswith("{"):
                    state[k] = json.loads(v)
                elif v in {"True", "False"}:
                    state[k] = v == "True"
                else:
                    try:
                        state[k] = float(v) if "." in v else int(v)
                    except Exception:
                        state[k] = v
            return state
        except Exception:
            return {}

    def list_active_signals(self) -> List[str]:
        try:
            return sorted(list(self.redis.smembers("quanta.active_signals")))
        except Exception:
            return []

    def close_signal(self, signal_id: str) -> None:
        try:
            self.redis.srem("quanta.active_signals", signal_id)
            self.redis.hset(f"quanta.signal:{signal_id}", mapping={"status": "closed", "updated_at": str(int(time.time()))})
        except Exception:
            raise

    def get_trade_count(self) -> int:
        try:
            value = self.redis.get("quanta.trade_count")
            return int(value) if value else 0
        except Exception:
            return 0

    def increment_trade_count(self) -> int:
        try:
            return int(self.redis.incr("quanta.trade_count"))
        except Exception:
            raise
