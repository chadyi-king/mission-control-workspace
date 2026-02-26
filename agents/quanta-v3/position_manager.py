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
                return (current_price - entry) * 10   # 1 ch-pip = $0.10
            return (entry - current_price) * 10   # 1 ch-pip = $0.10
        except Exception:
            return 0.0

    def _close_partial(self, trade_id: str, units: int) -> None:
        try:
            if units > 0:
                self.oanda.close_trade_units(trade_id, str(units))
        except Exception as exc:
            self.logger.exception("partial close failed: %s", exc)

    def _close_partial_multi(self, trade_ids: List[str], close_units_total: int, remaining_units: int) -> int:
        if not trade_ids or close_units_total <= 0 or remaining_units <= 0:
            return 0
        close_units_total = min(close_units_total, remaining_units)
        per_trade = max(int(close_units_total / len(trade_ids)), 1)
        closed = 0
        for trade_id in trade_ids:
            if closed >= close_units_total:
                break
            units = min(per_trade, close_units_total - closed)
            self._close_partial(trade_id, units)
            closed += units
        return closed

    def _price_hits_tp(self, direction: str, price: float, tp_price: float) -> bool:
        if direction == "BUY":
            return price >= tp_price
        return price <= tp_price

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

                    # ── Resolve order IDs → trade IDs after limit orders fill ──
                    # When orders were placed as LIMIT, state["trade_ids"] holds
                    # ORDER IDs.  Once they fill, OANDA creates new TRADE IDs.
                    # We find them by the client tag we set: qv3-{message_id}-tierN
                    if not active_ids and state.get("message_id"):
                        tag_prefix = f"qv3-{state['message_id']}"
                        try:
                            resolved = self.oanda.get_trade_ids_by_tag_prefix(tag_prefix)
                            if resolved:
                                self.logger.info(
                                    "position_manager resolved order→trade IDs "
                                    "for msg_id=%s: %s", state["message_id"], resolved
                                )
                                state["trade_ids"] = resolved
                                trade_ids = resolved
                                active_ids = [tid for tid in trade_ids if tid in live_ids]
                        except Exception:
                            self.logger.exception("Failed to resolve trade IDs for msg_id=%s", state.get("message_id"))

                    if not active_ids:
                        # Don't mark closed if LIMIT orders are still pending (waiting to fill)
                        has_pending = False
                        if state.get("message_id"):
                            tag_prefix = f"qv3-{state['message_id']}"
                            try:
                                pending_ids = self.oanda.get_order_ids_by_tag_prefix(tag_prefix)
                                if pending_ids:
                                    has_pending = True
                                    self.logger.info(
                                        "position_manager: no open trades yet — "
                                        "%d pending order(s) for msg_id=%s, waiting for fill",
                                        len(pending_ids), state["message_id"],
                                    )
                            except Exception:
                                self.logger.exception(
                                    "Failed to check pending orders for msg_id=%s",
                                    state.get("message_id"),
                                )
                        if not has_pending:
                            state["status"] = "closed"
                        updated.append(state)
                        continue

                    price = self.oanda.get_price(state["symbol"])
                    pips = self._pips_profit(state, price)
                    original_units = int(state["original_units"])
                    remaining_units = int(state["remaining_units"])
                    hit = set(state.get("tp_levels_hit", []))

                    tp_levels = state.get("tp_levels") or []
                    if tp_levels:
                        ordered = sorted(tp_levels) if state["direction"] == "BUY" else sorted(tp_levels, reverse=True)
                        first_tp = ordered[0]
                        last_tp = ordered[-1]
                        for tp_price in ordered:
                            if tp_price in hit:
                                continue
                            if self._price_hits_tp(state["direction"], price, tp_price):
                                close_units = max(int(original_units * 0.10), 1)
                                closed = self._close_partial_multi(active_ids, close_units, remaining_units)
                                remaining_units = max(remaining_units - closed, 0)
                                hit.add(tp_price)
                                if tp_price == first_tp:
                                    for trade_id in active_ids:
                                        self.oanda.update_trade_sl(trade_id, float(state["entry_price"]))
                                if tp_price == last_tp:
                                    state["runner_active"] = True
                    else:
                        for tp in self.TP_LEVELS:
                            if pips >= tp and tp not in hit:
                                close_units = max(int(original_units * 0.10), 1)
                                closed = self._close_partial_multi(active_ids, close_units, remaining_units)
                                remaining_units = max(remaining_units - closed, 0)
                                hit.add(tp)
                                if tp == 20:
                                    for trade_id in active_ids:
                                        self.oanda.update_trade_sl(trade_id, float(state["entry_price"]))
                                if tp == 100:
                                    state["runner_active"] = True

                    if state.get("runner_active"):
                        # Runner: every 100 channel pips past TP5 -> close 10% remaining
                        # 1 channel pip = $0.10, so 100 ch-pips = $10.00 price move
                        RUNNER_STEP_PRICE = 10.0   # $10 per 100 channel pips
                        RUNNER_SL_TRAIL   = 10.0   # trail SL $10 behind milestone

                        entry_price = float(state["entry_price"])
                        if state["direction"] == "BUY":
                            price_gain = price - entry_price
                        else:
                            price_gain = entry_price - price

                        runner_steps_should_be = int(price_gain // RUNNER_STEP_PRICE)
                        runner_steps_hit = int(state.get("runner_steps_hit", 0))
                        while runner_steps_hit < runner_steps_should_be and remaining_units > 0:
                            close_units = max(int(remaining_units * 0.10), 1)
                            closed = self._close_partial_multi(active_ids, close_units, remaining_units)
                            remaining_units = max(remaining_units - closed, 0)
                            runner_steps_hit += 1
                        state["runner_steps_hit"] = runner_steps_hit

                        # Trail SL: $10 behind latest milestone
                        milestone_gain = runner_steps_hit * RUNNER_STEP_PRICE
                        if state["direction"] == "BUY":
                            trailing_sl = entry_price + milestone_gain - RUNNER_SL_TRAIL
                        else:
                            trailing_sl = entry_price - milestone_gain + RUNNER_SL_TRAIL
                        state["trailing_sl"] = trailing_sl
                        for trade_id in active_ids:
                            self.oanda.update_trade_sl(trade_id, trailing_sl)

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
