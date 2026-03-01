import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv as _load_dotenv
    _DOTENV_AVAILABLE = True
except ImportError:
    _DOTENV_AVAILABLE = False


@dataclass(frozen=True)
class Settings:
    telegram_api_id: int
    telegram_api_hash: str
    telegram_phone: str
    telegram_session_file: str
    telegram_string_session: str
    telegram_channel_name: str
    oanda_account_id: str
    oanda_api_key: str
    oanda_environment: str
    state_file: Path
    open_trades_file: Path
    log_file: Path
    redis_url: str
    signal_stream: str
    signal_group: str
    signal_consumer: str
    pending_idle_ms: int
    event_stream: str

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
        # Load .env from the project root so all env vars (including
        # TELEGRAM_STRING_SESSION) are available before any os.getenv() call.
        _env_path = Path(__file__).resolve().parent / ".env"
        if _DOTENV_AVAILABLE and _env_path.exists():
            _load_dotenv(_env_path, override=False)

        # If environment variables aren't set (e.g., dev machine), try a local
        # `runtime_secrets.py` as a fallback so keys can be loaded without
        # changing code elsewhere. Do NOT print or log secret values here.
        if not os.getenv("OANDA_ENVIRONMENT"):
            try:
                import importlib

                rs = importlib.import_module("runtime_secrets")
                # only set env vars if they are present in the module
                for k in ("OANDA_ENVIRONMENT", "OANDA_ACCOUNT_ID", "OANDA_API_KEY", "TELEGRAM_API_ID", "TELEGRAM_API_HASH", "TELEGRAM_PHONE"):
                    if hasattr(rs, k):
                        os.environ.setdefault(k, str(getattr(rs, k)))
            except Exception:
                # no runtime_secrets available; proceed and let _required_env raise
                pass

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
            telegram_string_session=os.getenv("TELEGRAM_STRING_SESSION", "").strip(),
            telegram_channel_name=os.getenv("TELEGRAM_CHANNEL_NAME", "🚀 CallistoFx Premium Channel 🚀"),
            oanda_account_id=_required_env("OANDA_ACCOUNT_ID"),
            oanda_api_key=_required_env("OANDA_API_KEY"),
            oanda_environment=env,
            state_file=base / "telegram_state.json",
            open_trades_file=base / "open_trades.json",
            log_file=base / "logs" / "quanta.log",
            redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            signal_stream=os.getenv("SIGNAL_STREAM", "quanta.signals"),
            signal_group=os.getenv("SIGNAL_GROUP", "quanta"),
            signal_consumer=os.getenv("SIGNAL_CONSUMER", "quanta-executor"),
            pending_idle_ms=int(os.getenv("PENDING_IDLE_MS", "60000")),
            event_stream=os.getenv("EVENT_STREAM", "quanta.events"),
        )
    except Exception:
        raise
