import json
import logging
import time

from config import load_settings
from oanda_client import OandaClient
from redis_backbone import RedisBackbone
from reporter import Reporter
from risk_manager import RiskManager
from trade_manager import TradeManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("quanta.executor")


class SignalExecutor:
    def __init__(self):
        self.settings = load_settings()
        self.store = RedisBackbone(self.settings.redis_url)
        self.store.ensure_group(self.settings.signal_stream, self.settings.signal_group)
        self.reporter = Reporter(self.store, self.settings.event_stream)
        self.oanda = OandaClient(
            self.settings.oanda_account_id,
            self.settings.oanda_api_key,
            self.settings.oanda_base_url,
        )
        self.trade_manager = TradeManager(self.oanda, self.store, RiskManager(self.store))

    def _handle_message(self, msg_id: str, fields: dict) -> None:
        signal = json.loads(fields["signal"])
        signal_id = signal["signal_id"]

        if self.store.is_processed_signal(signal_id):
            logger.info("Duplicate signal skipped: %s", signal_id)
            self.store.ack(self.settings.signal_stream, self.settings.signal_group, msg_id)
            return

        self.reporter.emit("signal", {"signal_id": signal_id, "symbol": signal["symbol"]})
        result = self.trade_manager.execute_signal(signal)
        self.store.add_processed_signal(signal_id)
        self.store.ack(self.settings.signal_stream, self.settings.signal_group, msg_id)
        self.reporter.emit("trade", result)

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
                    self.reporter.emit("error", {"message_id": msg_id, "error": str(exc), "retry": True})

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
                        self.reporter.emit("error", {"message_id": msg_id, "error": str(exc), "retry": True})
            time.sleep(0.2)


if __name__ == "__main__":
    SignalExecutor().run_forever()
