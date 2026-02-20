import argparse
import asyncio
import threading
import time

from config import load_settings
from logger_setup import build_logger
from oanda_client import OandaClient
from position_manager import PositionManager
from redis_backbone import RedisState
from state_store import StateStore
from telegram_monitor import TelegramMonitor
from trade_manager import TradeManager


def start_monitor(settings, disk_state, redis_state, oanda, logger):
    try:
        monitor = TelegramMonitor(settings, disk_state, redis_state, TradeManager(oanda, redis_state), logger)
        asyncio.run(monitor.run_forever())
    except Exception as exc:
        logger.error(exc)
        raise


def start_manager(settings, redis_state, oanda, logger):
    try:
        PositionManager(oanda, redis_state, logger).run_forever(settings.heartbeat_seconds)
    except Exception as exc:
        logger.error(exc)
        raise


def run_supervisor(role: str):
    settings = load_settings()
    logger = build_logger(str(settings.log_file))
    oanda = OandaClient(settings.oanda_account_id, settings.oanda_api_key, settings.oanda_base_url)
    redis_state = RedisState(settings.redis_url)
    disk_state = StateStore(settings.telegram_state_file)

    while True:
        try:
            if role == "monitor":
                start_monitor(settings, disk_state, redis_state, oanda, logger)
            elif role == "manager":
                start_manager(settings, redis_state, oanda, logger)
            else:
                t1 = threading.Thread(target=start_monitor, args=(settings, disk_state, redis_state, oanda, logger), daemon=True)
                t2 = threading.Thread(target=start_manager, args=(settings, redis_state, oanda, logger), daemon=True)
                t1.start()
                t2.start()
                while t1.is_alive() and t2.is_alive():
                    time.sleep(1)
                raise RuntimeError("worker stopped")
        except Exception as exc:
            logger.error(exc)
            time.sleep(3)


def main():
    parser = argparse.ArgumentParser(description="QUANTA v3")
    parser.add_argument("--role", choices=["monitor", "manager", "all"], default="all")
    args = parser.parse_args()
    run_supervisor(args.role)


if __name__ == "__main__":
    main()
