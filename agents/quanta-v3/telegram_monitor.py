import asyncio
from collections import deque
from typing import Optional

from telethon import TelegramClient

from signal_parser import SignalParser
from trade_manager import TradeManager


class TelegramMonitor:
    def __init__(self, settings, disk_state, redis_state, trade_manager: TradeManager, logger):
        self.settings = settings
        self.disk_state = disk_state
        self.redis_state = redis_state
        self.trade_manager = trade_manager
        self.log = logger
        self.parser = SignalParser()
        self.buffer = deque(maxlen=50)
        self.client: Optional[TelegramClient] = None

    def _build_client(self) -> TelegramClient:
        try:
            return TelegramClient(
                self.settings.telegram_session_file,
                self.settings.telegram_api_id,
                self.settings.telegram_api_hash,
                auto_reconnect=True,
                connection_retries=None,
                retry_delay=5,
            )
        except Exception:
            raise

    async def _resolve_channel_id(self) -> int:
        try:
            st = self.disk_state.load()
            if st.get("channel_id"):
                return int(st["channel_id"])
            entity = await self.client.get_entity(self.settings.telegram_channel_name)
            st["channel_id"] = int(entity.id)
            self.disk_state.save(st)
            return int(entity.id)
        except Exception:
            raise

    async def _prime_buffer(self, channel_id: int):
        try:
            st = self.disk_state.load()
            last_id = int(st.get("last_processed_id", 0))
            async for msg in self.client.iter_messages(channel_id, limit=50):
                self.buffer.appendleft(msg)
            async for msg in self.client.iter_messages(channel_id, min_id=last_id, reverse=True):
                self.buffer.append(msg)
        except Exception as e:
            self.log.error(e)

    async def _poll_once(self, channel_id: int):
        try:
            st = self.disk_state.load()
            last_id = int(st.get("last_processed_id", 0))
            async for msg in self.client.iter_messages(channel_id, min_id=last_id, reverse=True):
                self.buffer.append(msg)
                if int(msg.id) <= last_id:
                    continue
                parsed = self.parser.parse(msg.message or "", message_id=int(msg.id))
                if not parsed:
                    continue
                if self.redis_state.is_processed_signal(parsed.signal_id):
                    st["last_processed_id"] = int(msg.id)
                    self.disk_state.save(st)
                    continue

                self.trade_manager.execute_signal(parsed, int(msg.id))
                self.redis_state.mark_processed_signal(parsed.signal_id)
                st["last_processed_id"] = int(msg.id)
                self.disk_state.save(st)
                self.log.info("signal received and order placed msg_id=%s signal_id=%s", msg.id, parsed.signal_id)
        except Exception as e:
            self.log.error(e)

    async def run_forever(self):
        try:
            self.client = self._build_client()
            await self.client.start(phone=self.settings.telegram_phone)
            channel_id = await self._resolve_channel_id()
            await self._prime_buffer(channel_id)
            self.log.info("telegram monitor polling started for channel=%s", channel_id)
            while True:
                await self._poll_once(channel_id)
                await asyncio.sleep(3)
        except Exception as e:
            self.log.error(e)
            raise
