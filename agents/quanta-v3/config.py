import os
from dataclasses import dataclass
from pathlib import Path


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
    state_file: Path
    open_trades_file: Path
    log_file: Path

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
            state_file=base / "telegram_state.json",
            open_trades_file=base / "open_trades.json",
            log_file=base / "logs" / "quanta.log",
        )
    except Exception:
        raise
