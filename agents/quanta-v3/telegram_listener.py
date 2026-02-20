from telethon import TelegramClient, events

from redis_backbone import RedisState
from runtime_secrets import TELEGRAM_API_HASH, TELEGRAM_API_ID, TELEGRAM_PHONE
from signal_parser import SignalParser
from trade_manager import TradeManager


class TelegramListener:
    def __init__(self, settings, state: RedisState, trade_manager: TradeManager, logger):
        self.settings = settings
        self.state = state
        self.trade_manager = trade_manager
        self.logger = logger
        self.parser = SignalParser()
        self.client = TelegramClient(
            "quanta_session",
            TELEGRAM_API_ID,
            TELEGRAM_API_HASH,
            auto_reconnect=True,
            connection_retries=None,
            retry_delay=5,
        )

    @staticmethod
    def _title_matches_channel(title: str) -> bool:
        try:
            t = (title or "").lower()
            return ("callistofx" in t) or ("premium" in t)
        except Exception:
            return False

    async def _resolve_channel_id(self) -> int:
        try:
            st = self.state.get_telegram_state()
            if st.get("channel_id"):
                return int(st["channel_id"])

            async for dialog in self.client.iter_dialogs():
                name = getattr(dialog, "name", "") or ""
                if self._title_matches_channel(name):
                    st["channel_id"] = int(dialog.id)
                    self.state.set_telegram_state(st)
                    self.logger.info("resolved listener channel by fuzzy title match name=%s id=%s", name, dialog.id)
                    return int(dialog.id)

            entity = await self.client.get_entity(self.settings.telegram_channel_name)
            st["channel_id"] = int(entity.id)
            self.state.set_telegram_state(st)
            return int(entity.id)
        except Exception:
            raise

    async def run(self) -> None:
        try:
            await self.client.start(phone=TELEGRAM_PHONE)
            channel_id = await self._resolve_channel_id()

            @self.client.on(events.NewMessage(chats=channel_id))
            async def on_message(event):
                try:
                    st = self.state.get_telegram_state()
                    message_id = int(event.message.id)
                    if message_id <= int(st.get("last_processed_message_id", 0)):
                        return

                    parsed = self.parser.parse(event.raw_text or "", message_id=message_id)
                    if not parsed:
                        self.logger.info("ignored non-trade message_id=%s", message_id)
                        st["last_processed_message_id"] = message_id
                        self.state.set_telegram_state(st)
                        return
                    if self.state.is_processed_signal(parsed.signal_id):
                        self.logger.info("duplicate signal ignored signal_id=%s", parsed.signal_id)
                        st["last_processed_message_id"] = message_id
                        self.state.set_telegram_state(st)
                        return

                    self.trade_manager.execute_signal(parsed, message_id)
                    self.state.mark_processed_signal(parsed.signal_id)
                    st["last_processed_message_id"] = message_id
                    self.state.set_telegram_state(st)
                    self.logger.info("signal executed message_id=%s signal_id=%s", message_id, parsed.signal_id)
                except Exception as inner:
                    self.logger.exception("malformed or failed signal handler %s", inner)

            self.logger.info("telegram listener started channel_id=%s", channel_id)
            await self.client.run_until_disconnected()
        except Exception as exc:
            self.logger.exception("telegram listener crash %s", exc)
            raise
