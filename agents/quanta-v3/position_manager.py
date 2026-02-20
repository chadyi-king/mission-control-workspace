import time
from typing import Dict, List

from oanda_client import OandaClient


class PositionManager:
    TP_LEVELS = [20, 40, 60, 80, 100]

    def __init__(self, oanda: OandaClient, logger):
        self.oanda = oanda
        self.logger = logger

    def _pips_profit(self, trade_state: Dict, current_price: float) -> float:
        try:
            entry = float(trade_state["entry_price"])
            if trade_state["direction"] == "BUY":
                return (current_price - entry) * 100
            return (entry - current_price) * 100
        except Exception:
            return 0.0

    def _close_partial(self, trade_id: str, units: int) -> None:
        try:
            if units > 0:
                self.oanda.close_trade_units(trade_id, str(units))
        except Exception as exc:
            self.logger.exception("partial close failed: %s", exc)

    def manage_once(self, open_trades_state: List[Dict]) -> List[Dict]:
        try:
            live_trades = self.oanda.list_open_trades()
            live_ids = {t["id"] for t in live_trades}
            updated = []
            for state in open_trades_state:
                try:
                    if state.get("status") == "closed":
                        updated.append(state)
                        continue
                    trade_ids = [str(x) for x in state.get("trade_ids", [])]
                    active_ids = [tid for tid in trade_ids if tid in live_ids]
                    if not active_ids:
                        state["status"] = "closed"
                        updated.append(state)
                        continue

                    price = self.oanda.get_price(state["symbol"])
                    pips = self._pips_profit(state, price)
                    original_units = int(state["original_units"])
                    remaining_units = int(state["remaining_units"])
                    hit = set(state.get("tp_levels_hit", []))

                    for tp in self.TP_LEVELS:
                        if pips >= tp and tp not in hit:
                            close_units = max(int(original_units * 0.10), 1)
                            self._close_partial(active_ids[0], close_units)
                            remaining_units = max(remaining_units - close_units, 0)
                            hit.add(tp)
                            if tp == 20:
                                self.oanda.update_trade_sl(active_ids[0], float(state["entry_price"]))
                            if tp == 100:
                                state["runner_active"] = True

                    if state.get("runner_active"):
                        runner_steps_should_be = int(max(0, (pips - 100)) // 100)
                        runner_steps_hit = int(state.get("runner_steps_hit", 0))
                        while runner_steps_hit < runner_steps_should_be and remaining_units > 0:
                            close_units = max(int(remaining_units * 0.10), 1)
                            self._close_partial(active_ids[0], close_units)
                            remaining_units = max(remaining_units - close_units, 0)
                            runner_steps_hit += 1
                        state["runner_steps_hit"] = runner_steps_hit

                        trailing_sl = price - 1.0 if state["direction"] == "BUY" else price + 1.0
                        state["trailing_sl"] = trailing_sl
                        self.oanda.update_trade_sl(active_ids[0], trailing_sl)

                    state["remaining_units"] = remaining_units
                    state["tp_levels_hit"] = sorted(list(hit))
                    if remaining_units <= 0:
                        state["status"] = "closed"
                    updated.append(state)
                except Exception as exc:
                    self.logger.exception("manage trade failed: %s", exc)
                    updated.append(state)
            return updated
        except Exception as exc:
            self.logger.exception("manage_once failed: %s", exc)
            return open_trades_state

    def run_loop(self, load_fn, save_fn, sleep_seconds: int = 5):
        try:
            while True:
                states = load_fn()
                updated = self.manage_once(states)
                save_fn(updated)
                time.sleep(sleep_seconds)
        except Exception as exc:
            self.logger.exception("position loop crash: %s", exc)
            raise
