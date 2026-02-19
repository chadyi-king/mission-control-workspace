import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from runtime_secrets import *


CHANNEL_PIP_SIZE = {
    "XAUUSD": 0.1,
    "XAGUSD": 0.01,
    "EURUSD": 0.0001,
    "GBPUSD": 0.0001,
    "USDJPY": 0.01,
    "AUDUSD": 0.0001,
    "USDCAD": 0.0001,
    "NZDUSD": 0.0001,
    "NZDJPY": 0.01,
    "BTCUSD": 1.0,
    "WTI": 0.01,
    "BRENT": 0.01,
}


def channel_pips_to_price(symbol: str, pips: float) -> float:
    try:
        return float(pips) * CHANNEL_PIP_SIZE.get(symbol.upper(), 0.0001)
    except Exception:
        return float(pips) * 0.0001


def _build_redis_url() -> str:
    try:
        parsed = urlparse(UPSTASH_REDIS_REST_URL)
        host = parsed.netloc
        if not host:
            raise RuntimeError("Invalid UPSTASH_REDIS_REST_URL")
        default_redis = f"rediss://default:{UPSTASH_REDIS_REST_TOKEN}@{host}:6379"
        return os.getenv("REDIS_URL", default_redis)
    except Exception:
        raise


@dataclass(frozen=True)
class Settings:
    telegram_api_id: int
    telegram_api_hash: str
    telegram_phone: str
    telegram_session_file: str
    telegram_channel_name: str
    oanda_account_id: str
    oanda_api_key: str
    oanda_environment: str
    redis_url: str
    heartbeat_seconds: int
    log_file: Path
    telegram_state_file: Path

    @property
    def oanda_base_url(self) -> str:
        if self.oanda_environment == "LIVE":
            return "https://api-fxtrade.oanda.com"
        return "https://api-fxpractice.oanda.com"


def load_settings() -> Settings:
    try:
        env = str(OANDA_ENVIRONMENT).upper()
        if env not in {"LIVE", "PRACTICE"}:
            raise RuntimeError("OANDA_ENVIRONMENT must be LIVE or PRACTICE")
        base = Path(__file__).resolve().parent
        (base / "logs").mkdir(exist_ok=True)
        return Settings(
            telegram_api_id=int(TELEGRAM_API_ID),
            telegram_api_hash=str(TELEGRAM_API_HASH),
            telegram_phone=str(TELEGRAM_PHONE),
            telegram_session_file=os.getenv("TELEGRAM_SESSION_FILE", str(base / "quanta_v3.session")),
            telegram_channel_name=os.getenv("TELEGRAM_CHANNEL_NAME", "🚀 CallistoFx Premium Channel 🚀"),
            oanda_account_id=str(OANDA_ACCOUNT_ID),
            oanda_api_key=str(OANDA_API_KEY),
            oanda_environment=env,
            redis_url=_build_redis_url(),
            heartbeat_seconds=int(os.getenv("QUANTA_HEARTBEAT_SECONDS", "5")),
            log_file=base / "logs" / "quanta.log",
            telegram_state_file=base / "telegram_state.json",
        )
    except Exception:
        raise
