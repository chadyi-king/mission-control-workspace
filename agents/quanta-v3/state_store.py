import json
from pathlib import Path
from typing import Any, Dict


class StateStore:
    def __init__(self, state_file: Path):
        self.state_file = state_file

    def load(self) -> Dict[str, Any]:
        try:
            if not self.state_file.exists():
                return {"channel_id": None, "last_processed_id": 0}
            return json.loads(self.state_file.read_text())
        except Exception:
            return {"channel_id": None, "last_processed_id": 0}

    def save(self, payload: Dict[str, Any]) -> None:
        try:
            self.state_file.write_text(json.dumps(payload, indent=2))
        except Exception:
            raise
