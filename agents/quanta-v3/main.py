import argparse
import asyncio
import threading
import time
import os
import sys
import fcntl

from config import load_settings
from logger_setup import build_logger
from oanda_client import OandaClient
from position_manager import PositionManager
from executor import SignalExecutor
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


def start_executor(logger):
    try:
        SignalExecutor().run_forever()
    except Exception as exc:
        logger.exception("executor thread crash: %s", exc)
        raise


def run_supervisor(role: str):
    settings = load_settings()
    logger = build_logger(str(settings.log_file))
    store = StateStore(settings.state_file, settings.open_trades_file)
    try:
        from redis_backbone import RedisBackbone

        store.redis_backbone = RedisBackbone(settings.redis_url)
    except Exception:
        store.redis_backbone = None

    # DRY_RUN: can be controlled via env var DRY_RUN (1/0 or true/false)
    dry_run_env = os.getenv("DRY_RUN", "1").lower()
    dry_run = dry_run_env in ("1", "true", "yes", "y")

    oanda = OandaClient(settings.oanda_account_id, settings.oanda_api_key, settings.oanda_base_url, dry_run=dry_run)

    while True:
        try:
            if role == "listener":
                start_listener(settings, store, oanda, logger)
            elif role == "manager":
                start_manager(settings, store, oanda, logger)
            elif role == "executor":
                start_executor(logger)
            else:
                threads: dict = {}

                def _ensure_thread(name, target, args):
                    """Start the named thread only if it is not already alive."""
                    t = threads.get(name)
                    if t is None or not t.is_alive():
                        t = threading.Thread(target=target, args=args, daemon=True, name=name)
                        t.start()
                        threads[name] = t
                        logger.info("supervisor started thread: %s", name)
                    return t

                while True:
                    _ensure_thread("listener", start_listener, (settings, store, oanda, logger))
                    _ensure_thread("manager",  start_manager,  (settings, store, oanda, logger))
                    _ensure_thread("executor", start_executor, (logger,))
                    time.sleep(3)
                    dead = [n for n, t in threads.items() if not t.is_alive()]
                    if dead:
                        logger.warning("supervisor: thread(s) died and will be restarted: %s", dead)
        except Exception as exc:
            logger.exception("supervisor restarting after crash: %s", exc)
            time.sleep(3)


def main():
    lock_path = "/tmp/quanta-v3.supervisor.lock"
    lock_file = open(lock_path, "w")
    try:
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("quanta-v3 is already running (lock held). Exiting.")
        sys.exit(1)

    lock_file.write(str(os.getpid()))
    lock_file.flush()

    parser = argparse.ArgumentParser(description="QUANTA v3")
    parser.add_argument("--role", choices=["listener", "manager", "executor", "all"], default="all")
    parser.add_argument("--dry-run", dest="dry_run", choices=["true", "false", "1", "0"], help="Override DRY_RUN env (true/false)")
    args = parser.parse_args()

    # CLI override for DRY_RUN
    if args.dry_run is not None:
        val = args.dry_run.lower()
        os.environ["DRY_RUN"] = "1" if val in ("true", "1") else "0"

    try:
        run_supervisor(args.role)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
