import math
import time
from typing import Dict, List

from config import channel_pips_to_price
from oanda_client import OandaClient
from redis_backbone import RedisState, event_payload


class PositionManager:
    TP_LEVELS = [20, 40, 60, 80, 100]

    def __init__(self, oanda: OandaClient, state: RedisState, logger):
        self.oanda = oanda
        self.state = state
        self.log = logger

    def _emit(self, event_type: str, data: Dict) -> None:
        try:
            self.state.publish_event("quanta.events", event_payload(event_type, data))
        except Exception as e:
            self.log.error(e)

    def _trades_for_signal(self, signal_id: str, trades: List[Dict]) -> List[Dict]:
        try:
            out: List[Dict] = []
            for trade in trades:
                tag = (trade.get("clientExtensions") or {}).get("tag", "")
                if signal_id in tag:
                    out.append(trade)
            return out
        except Exception as e:
            self.log.error(e)
            return []

    def _close_across_trades(self, trades: List[Dict], units_to_close: int) -> int:
        try:
            remaining = max(int(units_to_close), 0)
            closed = 0
            for trade in trades:
                if remaining <= 0:
                    break
                trade_units = abs(int(float(trade.get("currentUnits", trade.get("initialUnits", 0)))))
                if trade_units <= 0:
                    continue
                close_now = min(trade_units, remaining)
                self.oanda.close_trade_units(str(trade["id"]), str(close_now))
                remaining -= close_now
                closed += close_now
            return closed
        except Exception as e:
            self.log.error(e)
            return 0

    def _move_all_sls(self, trades: List[Dict], sl_price: float) -> None:
        try:
            for trade in trades:
                self.oanda.update_trade_sl(str(trade["id"]), sl_price)
        except Exception as e:
            self.log.error(e)

    def _tp_trigger_price(self, symbol: str, direction: str, first_entry: float, channel_pips: int) -> float:
        try:
            delta = channel_pips_to_price(symbol, channel_pips)
            return first_entry + delta if direction == "BUY" else first_entry - delta
        except Exception as e:
            self.log.error(e)
            return first_entry

    def _runner_sl_price(self, symbol: str, direction: str, first_entry: float, trigger_channel_pips: int) -> float:
        try:
            sl_pips_from_anchor = trigger_channel_pips - 100
            delta = channel_pips_to_price(symbol, sl_pips_from_anchor)
            return first_entry + delta if direction == "BUY" else first_entry - delta
        except Exception as e:
            self.log.error(e)
            return first_entry

    def _current_profit_channel_pips(self, symbol: str, direction: str, first_entry: float, current_price: float) -> float:
        try:
            move = (current_price - first_entry) if direction == "BUY" else (first_entry - current_price)
            one_pip_price = channel_pips_to_price(symbol, 1)
            if one_pip_price <= 0:
                return 0.0
            return move / one_pip_price
        except Exception:
            return 0.0

    def _hit_trigger(self, direction: str, current: float, trigger: float) -> bool:
        try:
            return current >= trigger if direction == "BUY" else current <= trigger
        except Exception:
            return False

    def manage_once(self) -> None:
        try:
            live = self.oanda.list_open_trades()
            for signal_id in self.state.list_active_signals():
                try:
                    signal_state = self.state.load_signal_state(signal_id)
                    if not signal_state or signal_state.get("status") == "closed":
                        continue

                    signal_trades = self._trades_for_signal(signal_id, live)
                    if not signal_trades:
                        self.state.close_signal(signal_id)
                        self._emit("trade_closed", {"signal_id": signal_id, "reason": "no_open_trades"})
                        continue

                    symbol = str(signal_state.get("symbol", ""))
                    direction = str(signal_state.get("direction", "BUY"))
                    first_entry = float(signal_state.get("first_entry_price", 0) or 0)
                    if first_entry <= 0:
                        first_entry = float(signal_trades[0].get("price", 0) or 0)
                        signal_state["first_entry_price"] = first_entry

                    current_price = self.oanda.get_price(symbol)
                    original_units = int(float(signal_state.get("original_total_units", signal_state.get("original_position_size", 0))))
                    remaining_units = int(float(signal_state.get("remaining_position_size", signal_state.get("remaining_total_units", 0))))

                    signal_state["stored_pip_distance"] = abs(current_price - first_entry) / max(self.oanda.get_pip_size(symbol), 1e-9)

                    for idx, level in enumerate(self.TP_LEVELS, start=1):
                        done_key = f"tp{idx}_done"
                        if bool(signal_state.get(done_key, False)):
                            continue
                        trigger = self._tp_trigger_price(symbol, direction, first_entry, level)
                        if not self._hit_trigger(direction, current_price, trigger):
                            continue

                        close_units = max(int(original_units * 0.1), 1)
                        closed = self._close_across_trades(signal_trades, close_units)
                        if closed <= 0:
                            continue

                        remaining_units = max(remaining_units - closed, 0)
                        signal_state[done_key] = True
                        signal_state["tp_levels_hit"] = sorted(set(signal_state.get("tp_levels_hit", []) + [level]))
                        self._emit("tp_hit", {"signal_id": signal_id, "level": f"TP{idx}", "closed_units": closed})

                        if idx == 1:
                            self._move_all_sls(signal_trades, first_entry)
                            signal_state["current_trailing_sl"] = first_entry
                            signal_state["current_stop_loss"] = first_entry
                            self._emit("sl_moved_be", {"signal_id": signal_id, "sl": first_entry})

                        if idx == 5:
                            signal_state["runner_active"] = True
                            signal_state["runner_mode_active"] = True
                            signal_state["runner_next_trigger"] = 200
                            self._emit("runner_activated", {"signal_id": signal_id, "next_trigger_channel_pips": 200})

                    if bool(signal_state.get("runner_active", False)) and remaining_units > 0:
                        profit_pips = self._current_profit_channel_pips(symbol, direction, first_entry, current_price)
                        runner_step = int(math.floor(profit_pips / 100.0)) if profit_pips > 0 else 0
                        runner_trigger = runner_step * 100
                        last_runner_trigger = int(signal_state.get("last_runner_trigger", 100))

                        if runner_trigger >= 200 and runner_trigger > last_runner_trigger:
                            trigger_iter = last_runner_trigger + 100
                            while trigger_iter <= runner_trigger and remaining_units > 0:
                                runner_close = max(int(remaining_units * 0.1), 1)
                                closed = self._close_across_trades(signal_trades, runner_close)
                                if closed <= 0:
                                    break

                                remaining_units = max(remaining_units - closed, 0)
                                new_sl = self._runner_sl_price(symbol, direction, first_entry, trigger_iter)
                                self._move_all_sls(signal_trades, new_sl)
                                signal_state["current_trailing_sl"] = new_sl
                                signal_state["current_stop_loss"] = new_sl
                                signal_state["last_runner_trigger"] = trigger_iter
                                signal_state["runner_next_trigger"] = trigger_iter + 100

                                self._emit("runner_tp", {"signal_id": signal_id, "trigger_channel_pips": trigger_iter, "closed_units": closed})
                                self._emit("runner_sl_update", {"signal_id": signal_id, "new_sl": new_sl})
                                self.log.info("runner step applied signal_id=%s trigger=%s sl=%s", signal_id, trigger_iter, new_sl)

                                trigger_iter += 100

                    signal_state["remaining_position_size"] = remaining_units
                    signal_state["remaining_total_units"] = remaining_units
                    if remaining_units <= 0:
                        signal_state["status"] = "closed"
                        self.state.close_signal(signal_id)
                        self._emit("trade_closed", {"signal_id": signal_id, "reason": "position_fully_closed"})
                    else:
                        self.state.save_signal_state(signal_id, signal_state)
                except Exception as e:
                    self.log.error(e)
                    self._emit("error", {"signal_id": signal_id, "error": str(e)})
        except Exception as e:
            self.log.error(e)
            self._emit("error", {"error": str(e), "scope": "manage_once"})

    def run_forever(self, interval_seconds: int = 5) -> None:
        while True:
            try:
                self.manage_once()
            except Exception as e:
                self.log.error(e)
                self._emit("error", {"error": str(e), "scope": "run_forever"})
            time.sleep(interval_seconds)
