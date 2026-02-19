import json
import logging
import time

from config import load_settings
from oanda_client import OandaClient
from redis_backbone import RedisState
from trade_manager import TradeManager

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("quanta.executor")


class SignalExecutor:
    """Order transport layer: forwards risk-sized units without extra scaling."""

    def __init__(self):
        self.settings = load_settings()
        self.store = RedisState(self.settings.redis_url)
        self.oanda = OandaClient(
            self.settings.oanda_account_id,
            self.settings.oanda_api_key,
            self.settings.oanda_base_url,
        )
        self.trade_manager = TradeManager(self.oanda, self.store)

    def execute_parsed_signal(self, signal, message_id: int):
        try:
            # TradeManager already computes sized units from RiskManager.
            # Executor must not apply additional unit math.
            return self.trade_manager.execute_signal(signal, message_id)
        except Exception as exc:
            logger.error(exc)
            raise

    def run_forever(self):
        try:
            logger.info("executor started (transport mode)")
            while True:
                time.sleep(2)
        except Exception as exc:
            logger.error(exc)
            raise


if __name__ == "__main__":
    SignalExecutor().run_forever()
