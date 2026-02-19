import os
from dataclasses import dataclass
from pathlib import Path


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


def _required_env(name: str) -> str:
    try:
        value = os.getenv(name, "").strip()
        if not value:
            raise RuntimeError(f"Missing required env var: {name}")
        return value
    except Exception:
        raise


def load_settings() -> Settings:
    try:
        env = _required_env("OANDA_ENVIRONMENT").upper()
        if env not in {"LIVE", "PRACTICE"}:
            raise RuntimeError("OANDA_ENVIRONMENT must be LIVE or PRACTICE")
        base = Path(__file__).resolve().parent
        (base / "logs").mkdir(exist_ok=True)
        return Settings(
            telegram_api_id=int(_required_env("TELEGRAM_API_ID")),
            telegram_api_hash=_required_env("TELEGRAM_API_HASH"),
            telegram_phone=_required_env("TELEGRAM_PHONE"),
            telegram_session_file=os.getenv("TELEGRAM_SESSION_FILE", str(base / "quanta_v3.session")),
            telegram_channel_name=os.getenv("TELEGRAM_CHANNEL_NAME", "🚀 CallistoFx Premium Channel 🚀"),
            oanda_account_id=_required_env("OANDA_ACCOUNT_ID"),
            oanda_api_key=_required_env("OANDA_API_KEY"),
            oanda_environment=env,
            redis_url=_required_env("REDIS_URL"),
            heartbeat_seconds=int(os.getenv("QUANTA_HEARTBEAT_SECONDS", "5")),
            log_file=base / "logs" / "quanta.log",
            telegram_state_file=base / "telegram_state.json",
        )
    except Exception:
        raise
