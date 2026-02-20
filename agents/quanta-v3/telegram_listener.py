import asyncio
from telethon import TelegramClient, events

from signal_parser import SignalParser
from trade_manager import TradeManager


class TelegramExecutionBot:
    def __init__(self, settings, store, oanda, logger):
        self.settings = settings
        self.store = store
        self.oanda = oanda
        self.logger = logger
        self.parser = SignalParser()
        self.trade_manager = TradeManager(oanda)
        self.client = TelegramClient(
            settings.telegram_session_file,
            settings.telegram_api_id,
            settings.telegram_api_hash,
            auto_reconnect=True,
            connection_retries=None,
            retry_delay=5,
        )

    async def _resolve_channel_id(self) -> int:
        try:
            state = self.store.load_telegram_state()
            if state.get("channel_id"):
                return int(state["channel_id"])
            entity = await self.client.get_entity(self.settings.telegram_channel_name)
            state["channel_id"] = entity.id
            self.store.save_telegram_state(state)
            return int(entity.id)
        except Exception:
            raise

    def _extract_trade_ids(self, execution_payload) -> list:
        try:
            trade_ids = []
            for order_response in execution_payload.get("orders", []):
                fill = order_response.get("orderFillTransaction") or {}
                if fill.get("tradeOpened", {}).get("tradeID"):
                    trade_ids.append(fill["tradeOpened"]["tradeID"])
                for x in fill.get("tradesOpened", []):
                    if x.get("tradeID"):
                        trade_ids.append(x["tradeID"])
            return trade_ids
        except Exception:
            return []

    async def run(self):
        try:
            await self.client.start(phone=self.settings.telegram_phone)
            channel_id = await self._resolve_channel_id()

            @self.client.on(events.NewMessage(chats=channel_id))
            async def on_signal(event):
                try:
                    message_id = int(event.message.id)
                    state = self.store.load_telegram_state()
                    if message_id <= int(state.get("last_processed_message_id", 0)):
                        return

                    text = event.raw_text or ""
                    parsed = self.parser.parse(text)
                    if not parsed:
                        self.logger.info("Ignored non-signal or invalid message_id=%s", message_id)
                        return

                    execution = self.trade_manager.execute_three_tier(parsed, message_id)
                    trade_ids = self._extract_trade_ids(execution)
                    execution["trade_ids"] = trade_ids
                    execution["status"] = "open"

                    trades = self.store.load_open_trades()
                    trades.append(execution)
                    self.store.save_open_trades(trades)

                    state["last_processed_message_id"] = message_id
                    self.store.save_telegram_state(state)
                    self.logger.info("Executed signal from message %s", message_id)
                except Exception as exc:
                    self.logger.exception("signal handler failed: %s", exc)

            self.logger.info("Listener started for channel_id=%s", channel_id)
            await self.client.run_until_disconnected()
        except Exception as exc:
            self.logger.exception("listener crashed: %s", exc)
            raise
