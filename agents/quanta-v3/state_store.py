import json
from pathlib import Path
from typing import Any, Dict, List


class StateStore:
    def __init__(self, telegram_state_file: Path, open_trades_file: Path):
        self.telegram_state_file = telegram_state_file
        self.open_trades_file = open_trades_file
        self.redis_backbone = None
        self._open_trades_key = "quanta.open_trades"

    def load_telegram_state(self) -> Dict[str, Any]:
        try:
            if not self.telegram_state_file.exists():
                return {"channel_id": None, "last_processed_message_id": 0}
            return json.loads(self.telegram_state_file.read_text())
        except Exception:
            return {"channel_id": None, "last_processed_message_id": 0}

    def save_telegram_state(self, state: Dict[str, Any]) -> None:
        try:
            self.telegram_state_file.write_text(json.dumps(state, indent=2))
        except Exception:
            raise

    def load_open_trades(self) -> List[Dict[str, Any]]:
        try:
            if self.redis_backbone is not None:
                raw = self.redis_backbone.redis.get(self._open_trades_key)
                return json.loads(raw) if raw else []
            if not self.open_trades_file.exists():
                return []
            return json.loads(self.open_trades_file.read_text())
        except Exception:
            return []

    def save_open_trades(self, trades: List[Dict[str, Any]]) -> None:
        try:
            if self.redis_backbone is not None:
                self.redis_backbone.redis.set(self._open_trades_key, json.dumps(trades))
                return
            self.open_trades_file.write_text(json.dumps(trades, indent=2))
        except Exception:
            raise
