from dataclasses import dataclass
import os


def _as_bool(raw: str | None, default: bool = False) -> bool:
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class HeliosConfig:
    env: str
    host: str
    port: int
    replay_token: str
    redis_url: str | None
    postgres_dsn: str | None
    weaviate_url: str | None
    telegram_bot_token: str | None
    telegram_chat_id: str | None
    discord_webhook_url: str | None
    emit_notifications: bool


def load_config() -> HeliosConfig:
    return HeliosConfig(
        env=os.getenv("HELIOS_ENV", "development"),
        host=os.getenv("HELIOS_HOST", "0.0.0.0"),
        port=int(os.getenv("HELIOS_PORT", "8000")),
        replay_token=os.getenv("HELIOS_REPLAY_TOKEN", "replace_me"),
        redis_url=os.getenv("REDIS_URL"),
        postgres_dsn=os.getenv("POSTGRES_DSN"),
        weaviate_url=os.getenv("WEAVIATE_URL"),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN"),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID"),
        discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL"),
        emit_notifications=_as_bool(os.getenv("HELIOS_EMIT_NOTIFICATIONS"), default=False),
    )
