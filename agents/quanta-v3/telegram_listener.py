"""
Safer telegram listener module for quanta-v3.

This file is defensive so it can be imported in environments without Telethon.
It exposes `TelegramExecutionBot` which the supervisor can instantiate.
"""

import os
import json
from collections import deque
import time
import re
import logging
from datetime import timezone, timedelta
from typing import Any, Optional
from pathlib import Path

_SGT = timezone(timedelta(hours=8))  # Singapore Time = UTC+8

logger = logging.getLogger("quanta.telegram")
logger.addHandler(logging.NullHandler())

try:
    from telethon import TelegramClient, events
    from telethon.sessions import StringSession
    TELETHON_AVAILABLE = True
except Exception:
    TelegramClient = None
    events = None
    StringSession = None
    TELETHON_AVAILABLE = False

# minimal env defaults so module import doesn't crash tests
TELEGRAM_API_ID = int(os.getenv("TELEGRAM_API_ID", "0") or 0)
TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH", "")
TELEGRAM_PHONE = os.getenv("TELEGRAM_PHONE", "")
CONTROL_CHAT = os.getenv("CONTROL_CHAT")
STATE_FILE = os.getenv("TELEGRAM_STATE_FILE", "telegram_state.json")

KEYWORDS = [
    "buy", "buys", "buying",
    "sell", "sells", "selling",
    "tp", "takeprofit", "take profit",
    "sl", "stoploss", "stop loss",
    "zone", "entry", "entries", "entry-level", "entry level",
]


def load_state() -> dict:
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state: dict) -> None:
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception:
        logger.exception("Failed to save telegram state")


def normalize_text(s: Optional[str]) -> str:
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"[^\w\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def tolerant_signal_check(text: str) -> bool:
    s = normalize_text(text)
    if not s:
        return False
    count = sum(1 for k in KEYWORDS if k in s)
    tp_matches = re.findall(r"\btp\s*\d+", s)
    price_matches = re.findall(r"\b\d{2,6}(?:\.\d{1,5})?\b", s)
    if count >= 2:
        return True
    if tp_matches and price_matches:
        return True
    if any(k in s for k in ["buy", "sell", "entry", "zone"]) and price_matches:
        return True
    return False


class TelegramExecutionBot:
    def __init__(self, settings: Any, store: Any, oanda_client: Any, logger_obj: Optional[logging.Logger] = None):
        self.settings = settings
        self.store = store
        self.oanda = oanda_client
        self.logger = logger_obj or logger
        self.client = None
        self.parser = None
        self.trade_manager = None
        self.last50_snapshot_file = Path(self.settings.log_file).parent / "telegram_last50_messages.json"
        self.last50_messages = []

    def _ensure_parser(self) -> None:
        if not self.parser:
            from signal_parser import SignalParser

            self.parser = SignalParser()

    def _preview(self, text: str, limit: int = 140) -> str:
        s = (text or "").replace("\n", " ").strip()
        if len(s) <= limit:
            return s
        return s[: limit - 3] + "..."

    def _snapshot_last50(self, rows: list) -> None:
        try:
            payload = {
                "channel": getattr(self.settings, "telegram_channel_name", ""),
                "captured_at": int(time.time()),
                "count": len(rows),
                "messages": rows,
            }
            self.last50_snapshot_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
        except Exception:
            self.logger.exception("Failed writing last-50 snapshot file")

    def _build_snapshot_row(self, message_id: Optional[int], text: str) -> dict:
        self._ensure_parser()
        fuzzy_match = tolerant_signal_check(text)
        parse_ok = bool(self.parser.parse(text) if text else False)
        return {
            "message_id": int(message_id) if message_id is not None else None,
            "is_signal_candidate": bool(fuzzy_match),
            "parse_ok": bool(parse_ok),
            "text_preview": self._preview(text),
        }

    def _replace_last50(self, rows: list) -> None:
        self.last50_messages = list(rows)[-50:]
        self._snapshot_last50(self.last50_messages)

    def _append_last50(self, row: dict) -> None:
        dropped_id = None
        if len(self.last50_messages) >= 50:
            dropped = self.last50_messages.pop(0)
            dropped_id = dropped.get("message_id") if isinstance(dropped, dict) else None
        self.last50_messages.append(row)
        self._snapshot_last50(self.last50_messages)
        if dropped_id is not None:
            self.logger.debug("last50 rotated: dropped msg_id=%s  window_size=%s", dropped_id, len(self.last50_messages))

    def _log_message_event(
        self,
        message_id: Optional[int],
        text: str,
        is_old: bool,
        fuzzy: bool,
        parsed: Any,
        action: str,
        msg_date=None,
    ) -> None:
        """Emit one clean, human-readable block per message to the log."""
        source = "BACKFILL" if is_old else "LIVE    "
        if msg_date is not None:
            try:
                ts = msg_date.astimezone(_SGT).strftime("%b %d %H:%M:%S SGT")
            except Exception:
                ts = time.strftime("%b %d %H:%M:%S")
        else:
            ts = time.strftime("%b %d %H:%M:%S")
        preview = self._preview(text, 200)

        lines = [
            "",
            f"┌─ MSG #{message_id}  [{source}]  {ts}",
            f"│  TEXT   : {preview}",
        ]

        if parsed:
            tps = "  ".join(
                f"TP{i + 1}={level}" for i, level in enumerate(parsed.tp_levels or [])
            ) if parsed.tp_levels else "no TPs"
            entry_low = getattr(parsed, "entry_low", None)
            entry_high = getattr(parsed, "entry_high", None)
            entry_str = (
                f"{entry_low}\u2013{entry_high}"
                if entry_low and entry_high and entry_low != entry_high
                else str(entry_low or entry_high or "?")
            )
            lines.append(
                f"\u2502  SIGNAL : \u2713  {parsed.symbol}  {(parsed.direction or '').upper()}"
                f"  entry={entry_str}  SL={parsed.stop_loss}  {tps}"
            )
        elif fuzzy:
            lines.append("\u2502  SIGNAL : ~  looks like a signal but parser could not extract it")
        else:
            lines.append("\u2502  SIGNAL : \u2717  not a trading signal")

        action_map = {
            "PUBLISHED":    "\u2514\u2500 ACTION : \u2705 PUBLISHED   \u2192  trade queued for execution",
            "SKIP_OLD":     "\u2514\u2500 ACTION : \u23ed SKIPPED     \u2192  backfill / historical (read-only, no trade placed)",
            "NO_SIGNAL":    "\u2514\u2500 ACTION : \u2500  IGNORED     \u2192  message is not a trading signal",
            "PARSE_FAIL":   "\u2514\u2500 ACTION : \u26a0  IGNORED     \u2192  fuzzy match but parser could not confirm signal",
            "ALREADY_SEEN": "\u2514\u2500 ACTION : \u23ed SKIPPED     \u2192  already processed in a previous session",
            "NO_REDIS":     "\u2514\u2500 ACTION : \u2717 ERROR       \u2192  no Redis backbone; signal could not be queued",
        }
        lines.append(action_map.get(action, f"\u2514\u2500 ACTION : {action}"))
        lines.append("")
        self.logger.info("\n".join(lines))

    def _load_state(self) -> dict:
        if hasattr(self.store, "load_telegram_state"):
            return self.store.load_telegram_state()
        return load_state()

    def _save_state(self, state: dict) -> None:
        if hasattr(self.store, "save_telegram_state"):
            self.store.save_telegram_state(state)
        else:
            save_state(state)

    async def _handle_text(self, message_id: Optional[int], text: str, is_old: bool = False, msg_date=None, silent: bool = False):
        # ── Persist raw event to Redis (best-effort) ─────────────────────────
        try:
            if hasattr(self.store, "redis_backbone"):
                backbone = getattr(self.store, "redis_backbone")
                from redis_backbone import publish_event
                publish_event(backbone, "quanta.events", "telegram.message_received",
                              {"message_id": message_id, "text": (text or "")[:200], "is_old": bool(is_old)})
            elif hasattr(self.store, "push_signal_event"):
                self.store.push_signal_event(message_id, text, "detected_old" if is_old else "detected")
        except Exception:
            self.logger.exception("Failed to persist message %s", message_id)

        if not text or message_id is None:
            return

        self._ensure_parser()

        # ── Determine signal status ───────────────────────────────────────────
        fuzzy = tolerant_signal_check(text)
        parsed = self.parser.parse(text)

        # ── Check if already processed ────────────────────────────────────────
        state = self._load_state()
        last_id = int(state.get("last_processed_message_id", 0) or 0)
        already_seen = int(message_id) <= last_id

        # ── Determine action ──────────────────────────────────────────────────
        if already_seen:
            action = "ALREADY_SEEN"
        elif not parsed:
            action = "PARSE_FAIL" if fuzzy else "NO_SIGNAL"
        elif is_old:
            action = "SKIP_OLD"
        else:
            action = "PUBLISHED"

        # ── Emit the unified readable log block ───────────────────────────────
        if not silent:
            self._log_message_event(message_id, text, is_old, fuzzy, parsed, action, msg_date=msg_date)

        # ── Early exits ───────────────────────────────────────────────────────
        if already_seen:
            return
        if not parsed:
            try:
                if hasattr(self.store, "redis_backbone"):
                    backbone = getattr(self.store, "redis_backbone")
                    from redis_backbone import publish_event
                    publish_event(backbone, "quanta.events", "signal_ignored",
                                  {"message_id": message_id, "is_old": bool(is_old), "reason": action})
            except Exception:
                self.logger.exception("Failed to publish ignored event")
            return
        if is_old:
            return

        # ── Publish live signal ───────────────────────────────────────────────
        try:
            signal_payload = {
                "signal_id": f"tg-{message_id}",
                "message_id": int(message_id),
                "symbol": parsed.symbol,
                "direction": parsed.direction,
                "entry_low": parsed.entry_low,
                "entry_high": parsed.entry_high,
                "stop_loss": parsed.stop_loss,
                "tp_levels": parsed.tp_levels,
                "source": "telegram",
                "received_at": int(time.time()),
            }
            if hasattr(self.store, "redis_backbone"):
                backbone = getattr(self.store, "redis_backbone")
                from redis_backbone import publish_event
                backbone.publish_stream(self.settings.signal_stream, {"signal": signal_payload})
                publish_event(backbone, self.settings.event_stream, "signal_published",
                              {"message_id": message_id, "symbol": parsed.symbol})
                state["last_processed_message_id"] = int(message_id)
                self._save_state(state)
                try:
                    backbone.set_last_telegram_id(int(message_id))
                except Exception:
                    self.logger.exception("Failed to update redis last telegram id")
            else:
                self._log_message_event(message_id, text, is_old, fuzzy, parsed, "NO_REDIS", msg_date=msg_date)
        except Exception:
            self.logger.exception("Trade execution failed for message_id=%s", message_id)

    async def run(self):
        if not TELETHON_AVAILABLE:
            self.logger.info("Telethon not available; TelegramExecutionBot.run exiting")
            return

        string_session = getattr(self.settings, "telegram_string_session", "") or ""
        if string_session:
            self.client = TelegramClient(StringSession(string_session), self.settings.telegram_api_id, self.settings.telegram_api_hash)
            self.logger.info("Using TELEGRAM_STRING_SESSION for Telegram client (sqlite session file bypassed)")
        else:
            self.client = TelegramClient(self.settings.telegram_session_file, self.settings.telegram_api_id, self.settings.telegram_api_hash)
            self.logger.info("Using TELEGRAM_SESSION_FILE=%s", self.settings.telegram_session_file)

        await self.client.start(phone=self.settings.telegram_phone)
        # resolve channel by name (best-effort)
        target_name = getattr(self.settings, "telegram_channel_name", None)
        if not target_name:
            self.logger.error("No telegram_channel_name configured; exiting")
            await self.client.disconnect()
            return

        entity = None
        async for dialog in self.client.iter_dialogs():
            if dialog.name == target_name:
                entity = dialog
                break
        if not entity:
            lower = target_name.lower()
            async for dialog in self.client.iter_dialogs():
                if dialog.name and lower in dialog.name.lower():
                    entity = dialog
                    break
        if not entity:
            self.logger.error("Could not find channel: %s", target_name)
            await self.client.disconnect()
            return

        target_id = entity.id
        self.logger.info("Telegram channel resolved: name=%s id=%s", target_name, target_id)

        # prime buffer (no execution) and advance last_processed_message_id to newest seen
        newest_id = None
        backfill_messages = []
        prior_state = self._load_state()
        already_seen_before = int(prior_state.get("last_processed_message_id", 0) or 0) > 0
        # On restarts (already_seen_before=True) do a silent backfill — just update
        # state/buffer without printing 50 lines we already saw.
        silent_backfill = already_seen_before
        self.logger.info("")
        if silent_backfill:
            self.logger.info("━━  BACKFILL START  (silent — already seen before)  ━━━━━━━━━━━━━━━━━━━━━━━━━━")
        else:
            self.logger.info("━━  BACKFILL START  loading last 50 messages from [%s]  ━━━━━━━━━━━━━━━━━━━━━━━━━━", target_name)
        async for msg in self.client.iter_messages(target_id, limit=50):
            text = getattr(msg, "raw_text", None) or getattr(msg, "message", None) or ""
            message_id = getattr(msg, "id", None)
            row = self._build_snapshot_row(message_id, text)
            backfill_messages.append(row)
            if text:
                await self._handle_text(message_id, text, is_old=True, msg_date=getattr(msg, "date", None), silent=silent_backfill)
            if message_id is not None:
                newest_id = max(newest_id or 0, int(msg.id))

        # iter_messages returns newest->oldest; store oldest->newest and cap at 50
        self._replace_last50(list(reversed(backfill_messages)))
        self.logger.info("━━  BACKFILL DONE   %s messages loaded  newest_id=%s  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━", len(backfill_messages), newest_id)

        if newest_id:
            state = self._load_state()
            last_id = int(state.get("last_processed_message_id", 0) or 0)
            if last_id < newest_id:
                state["last_processed_message_id"] = newest_id
                self._save_state(state)

        @self.client.on(events.NewMessage(chats=target_id))
        async def _on_new_message(ev):
            text = getattr(ev.message, "message", "") or getattr(ev, "raw_text", "")
            message_id = getattr(ev.message, "id", None)
            self._append_last50(self._build_snapshot_row(message_id, text))
            await self._handle_text(message_id, text, is_old=False, msg_date=getattr(ev.message, "date", None))

        self.logger.info("")
        self.logger.info("━━  LISTENING   connected to [%s]  watching for new signals  ━━━━━━━━━━━━━━━━━━━━━━", target_name)
        await self.client.run_until_disconnected()
