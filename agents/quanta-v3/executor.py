import json
import logging
import time
import os

from config import load_settings
from oanda_client import OandaClient
from redis_backbone import RedisBackbone
from reporter import Reporter
from risk_manager import RiskManager
from trade_manager import TradeManager
from state_store import StateStore

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("quanta.executor")


class SignalExecutor:
    def __init__(self):
        self.settings = load_settings()
        self.store = RedisBackbone(self.settings.redis_url)
        self.store.ensure_group(self.settings.signal_stream, self.settings.signal_group)
        self.reporter = Reporter(self.store, self.settings.event_stream)
        self.state_store = StateStore(self.settings.state_file, self.settings.open_trades_file)
        self.state_store.redis_backbone = self.store
        self.oanda = OandaClient(
            self.settings.oanda_account_id,
            self.settings.oanda_api_key,
            self.settings.oanda_base_url,
            dry_run=os.getenv("DRY_RUN", "1").lower() in ("1", "true", "yes", "y"),
        )
        self.trade_manager = TradeManager(self.oanda, self.store, RiskManager(self.store), logger)

    def _handle_message(self, msg_id: str, fields: dict) -> None:
        signal = json.loads(fields["signal"])
        signal_id = signal["signal_id"]

        if self.store.is_processed_signal(signal_id):
            logger.info("Duplicate signal skipped: %s", signal_id)
            self.store.ack(self.settings.signal_stream, self.settings.signal_group, msg_id)
            return

        self.reporter.emit("signal", {"signal_id": signal_id, "symbol": signal["symbol"]})
        message_id = signal.get("message_id") or signal.get("signal_id") or "unknown"

        # Guard: skip if an active (non-closed) trade for this message_id already exists
        try:
            for t in self.state_store.load_open_trades():
                if str(t.get("message_id", "")) == str(message_id) and t.get("status") != "closed":
                    logger.info("message_id=%s already has active trade — skipping duplicate", message_id)
                    self.store.add_processed_signal(signal_id)
                    self.store.ack(self.settings.signal_stream, self.settings.signal_group, msg_id)
                    return
        except Exception:
            pass

        # Mark processed BEFORE executing so a crash mid-execution cannot replay the trade
        self.store.add_processed_signal(signal_id)

        result = self.trade_manager.execute_signal(signal, message_id)
        for trade_id in result.get("trade_ids", []):
            self.store.save_trade_state(trade_id, result)
        self.store.increment_trade_count()
        try:
            open_trades = self.state_store.load_open_trades()
            open_trades.append(result)
            self.state_store.save_open_trades(open_trades)
        except Exception as exc:
            self.reporter.emit("error", {"message_id": msg_id, "signal_id": signal_id, "error": str(exc), "retry": False})
        self.store.ack(self.settings.signal_stream, self.settings.signal_group, msg_id)
        self.reporter.emit("trade", result)
        self.reporter.emit("trade_executed", {"signal_id": signal_id, "message_id": message_id, "trade_ids": result.get("trade_ids", [])})

    def run_forever(self):
        self.reporter.emit("status", {"message": "executor started"})
        while True:
            stale = self.store.claim_stale(
                self.settings.signal_stream,
                self.settings.signal_group,
                self.settings.signal_consumer,
                min_idle_ms=self.settings.pending_idle_ms,
            )
            for msg_id, fields in stale:
                try:
                    self._handle_message(msg_id, fields)
                except Exception as exc:
                    signal_id = None
                    try:
                        signal_id = json.loads(fields.get("signal", "{}")).get("signal_id")
                    except Exception:
                        signal_id = None
                    self.reporter.emit("error", {"message_id": msg_id, "signal_id": signal_id, "error": str(exc), "retry": True})

            streams = self.store.read_group(
                self.settings.signal_stream,
                self.settings.signal_group,
                self.settings.signal_consumer,
            )
            for _, messages in streams:
                for msg_id, fields in messages:
                    try:
                        self._handle_message(msg_id, fields)
                    except Exception as exc:
                        signal_id = None
                        try:
                            signal_id = json.loads(fields.get("signal", "{}")).get("signal_id")
                        except Exception:
                            signal_id = None
                        self.reporter.emit("error", {"message_id": msg_id, "signal_id": signal_id, "error": str(exc), "retry": True})
            time.sleep(0.2)


if __name__ == "__main__":
    SignalExecutor().run_forever()
