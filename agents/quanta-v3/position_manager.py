import time
from typing import Dict, List, Optional

from oanda_client import OandaClient
from redis_backbone import RedisState
from config import channel_pips_to_price


class PositionManager:
    TP_LEVELS = [20, 40, 60, 80, 100]

    def __init__(self, oanda: OandaClient, state: RedisState, logger):
        self.oanda = oanda
        self.state = state
        self.log = logger

    def _trade_for_signal(self, signal_id: str, trades: List[Dict]) -> Optional[Dict]:
        try:
            for t in trades:
                tag = (t.get("clientExtensions") or {}).get("tag", "")
                if signal_id in tag:
                    return t
            return None
        except Exception:
            return None

    def _price_gain(self, direction: str, first_entry: float, current_price: float) -> float:
        try:
            if direction == "BUY":
                return current_price - first_entry
            return first_entry - current_price
        except Exception:
            return 0.0

    def _move_all_sls(self, signal_id: str, price: float, live_trades: List[Dict]) -> None:
        try:
            for t in live_trades:
                tag = (t.get("clientExtensions") or {}).get("tag", "")
                if signal_id in tag:
                    self.oanda.update_trade_sl(str(t["id"]), price)
        except Exception as e:
            self.log.error(e)

    def _close_units(self, trade_id: str, units: int) -> int:
        try:
            if units <= 0:
                return 0
            self.oanda.close_trade_units(trade_id, str(units))
            return units
        except Exception as e:
            self.log.error(e)
            return 0

    def manage_once(self):
        try:
            live = self.oanda.list_open_trades()
            for sid in self.state.list_active_signals():
                try:
                    s = self.state.load_signal_state(sid)
                    if not s or s.get("status") == "closed":
                        continue
                    tr = self._trade_for_signal(sid, live)
                    if not tr:
                        self.state.close_signal(sid)
                        continue

                    if float(s.get("first_entry_price", 0)) <= 0:
                        s["first_entry_price"] = float(tr.get("price", 0) or 0)
                        if s["first_entry_price"] <= 0:
                            continue

                    current = self.oanda.get_price(s["symbol"])
                    first = float(s["first_entry_price"])
                    gain_price = self._price_gain(s["direction"], first, current)
                    tp_hit = set(s.get("tp_levels_hit", []))
                    original = int(float(s["original_position_size"]))
                    remaining = int(float(s["remaining_position_size"]))

                    for level in self.TP_LEVELS:
                        trigger_price = channel_pips_to_price(s["symbol"], level)
                        if gain_price >= trigger_price and level not in tp_hit:
                            closed = self._close_units(str(tr["id"]), max(int(original * 0.1), 1))
                            remaining = max(remaining - closed, 0)
                            tp_hit.add(level)
                            if level == 20:
                                self._move_all_sls(sid, first, live)
                            if level == 100:
                                s["runner_mode_active"] = True
                                s["runner_trigger_price"] = current

                    if s.get("runner_mode_active"):
                        trigger = float(s.get("runner_trigger_price", current))
                        runner_step = channel_pips_to_price(s["symbol"], 100)
                        if runner_step <= 0:
                            runner_step = 0.0001
                        next_gain = self._price_gain(s["direction"], trigger, current)
                        while next_gain >= runner_step and remaining > 0:
                            closed = self._close_units(str(tr["id"]), max(int(remaining * 0.1), 1))
                            remaining = max(remaining - closed, 0)
                            if s["direction"] == "BUY":
                                trailing = current - runner_step
                                trigger = trigger + runner_step
                            else:
                                trailing = current + runner_step
                                trigger = trigger - runner_step
                            self._move_all_sls(sid, trailing, live)
                            s["current_trailing_sl"] = trailing
                            s["runner_trigger_price"] = trigger
                            next_gain = self._price_gain(s["direction"], trigger, current)

                    s["remaining_position_size"] = remaining
                    s["tp_levels_hit"] = sorted(tp_hit)
                    if remaining <= 0:
                        s["status"] = "closed"
                        self.state.close_signal(sid)
                    else:
                        self.state.save_signal_state(sid, s)
                except Exception as e:
                    self.log.error(e)
        except Exception as e:
            self.log.error(e)

    def run_forever(self, interval_seconds: int = 5):
        try:
            while True:
                self.manage_once()
                time.sleep(interval_seconds)
        except Exception as e:
            self.log.error(e)
            raise
