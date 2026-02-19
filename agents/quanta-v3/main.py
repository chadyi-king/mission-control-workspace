import argparse
import asyncio
import threading
import time

from config import load_settings
from logger_setup import build_logger
from oanda_client import OandaClient
from position_manager import PositionManager
from state_store import StateStore
from telegram_listener import TelegramExecutionBot


def start_listener(settings, store, oanda, logger):
    try:
        bot = TelegramExecutionBot(settings, store, oanda, logger)
        asyncio.run(bot.run())
    except Exception as exc:
        logger.exception("listener thread crash: %s", exc)
        raise


def start_manager(settings, store, oanda, logger):
    try:
        manager = PositionManager(oanda, logger)
        manager.run_loop(store.load_open_trades, store.save_open_trades)
    except Exception as exc:
        logger.exception("manager thread crash: %s", exc)
        raise


def run_supervisor(role: str):
    settings = load_settings()
    logger = build_logger(str(settings.log_file))
    store = StateStore(settings.state_file, settings.open_trades_file)
    oanda = OandaClient(settings.oanda_account_id, settings.oanda_api_key, settings.oanda_base_url)

    while True:
        try:
            if role == "listener":
                start_listener(settings, store, oanda, logger)
            elif role == "manager":
                start_manager(settings, store, oanda, logger)
            else:
                listener_thread = threading.Thread(target=start_listener, args=(settings, store, oanda, logger), daemon=True)
                manager_thread = threading.Thread(target=start_manager, args=(settings, store, oanda, logger), daemon=True)
                listener_thread.start()
                manager_thread.start()
                while listener_thread.is_alive() and manager_thread.is_alive():
                    time.sleep(1)
                raise RuntimeError("A worker thread exited")
        except Exception as exc:
            logger.exception("supervisor restarting after crash: %s", exc)
            time.sleep(3)


def main():
    parser = argparse.ArgumentParser(description="QUANTA v3")
    parser.add_argument("--role", choices=["listener", "manager", "all"], default="all")
    args = parser.parse_args()
    run_supervisor(args.role)


if __name__ == "__main__":
    main()
