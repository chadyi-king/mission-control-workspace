from typing import Dict, List, Optional, Tuple, Union
import math

from oanda_client import OandaClient
from signal_parser import ParsedSignal


class TradeManager:
    def __init__(self, oanda: OandaClient, store=None, risk_manager=None, logger=None):
        self.oanda = oanda
        self.store = store
        self.risk_manager = risk_manager
        self.logger = logger

    def _get_usd_sgd_rate(self) -> float:
        try:
            return float(self.oanda.get_price("USD_SGD"))
        except Exception:
            rate = float(self.oanda.get_price("SGD_USD"))
            if rate <= 0:
                raise RuntimeError("Invalid SGD_USD rate")
            return 1.0 / rate

    def _entry_prices(self, signal: ParsedSignal) -> List[float]:
        low = float(signal.entry_low)
        high = float(signal.entry_high)
        mid = (low + high) / 2.0
        if signal.direction == "SELL":
            return [high, mid, low]
        return [low, mid, high]

    def _sgd_loss_per_unit(self, entry_price: float, stop_loss: float, usd_sgd_rate: float) -> float:
        price_distance = abs(entry_price - stop_loss)
        if price_distance <= 0:
            raise RuntimeError("Invalid price distance for SL sizing")
        usd_loss_per_unit = price_distance
        return usd_loss_per_unit * usd_sgd_rate

    def compute_units(self, signal: ParsedSignal) -> Tuple[List[int], float, float]:
        if self.risk_manager is None:
            raise RuntimeError("risk_manager is required for sizing")

        summary = self.oanda.get_account_summary()
        nav = summary.get("NAV") or summary.get("balance") or summary.get("Balance")
        equity = float(nav) if nav is not None else None

        tier_risks = self.risk_manager.tier_risks(equity)
        usd_sgd_rate = self._get_usd_sgd_rate()

        entry_prices = self._entry_prices(signal)
        tier_units: List[int] = []
        total_expected_loss = 0.0
        for entry_price, risk_sgd in zip(entry_prices, tier_risks):
            sgd_loss_per_unit = self._sgd_loss_per_unit(entry_price, signal.stop_loss, usd_sgd_rate)
            units = int(math.floor(risk_sgd / sgd_loss_per_unit))
            if units <= 0:
                units = 1  # floor rounds to 0 (SL wider than tier risk budget); use 1-unit minimum
            tier_units.append(units)
            total_expected_loss += units * sgd_loss_per_unit

        return tier_units, usd_sgd_rate, total_expected_loss

    def _tier_units(self, total_units: int) -> List[int]:
        try:
            first = int(total_units * 0.33)
            second = int(total_units * 0.33)
            third = total_units - first - second
            return [first, second, third]
        except Exception:
            raise

    def _extract_trade_ids(self, responses: List[Dict]) -> List[str]:
        trade_ids: List[str] = []
        for resp in responses:
            if not isinstance(resp, dict):
                continue
            fill = resp.get("orderFillTransaction") or {}
            for key in ("tradeOpened", "tradeReduced", "tradeClosed"):
                if key in fill and isinstance(fill[key], dict) and fill[key].get("tradeID"):
                    trade_ids.append(str(fill[key]["tradeID"]))
            # fallback for simulated responses
            if "orderCreateTransaction" in resp and resp["orderCreateTransaction"].get("id"):
                trade_ids.append(str(resp["orderCreateTransaction"]["id"]))
        # preserve order, remove dups
        return list(dict.fromkeys(trade_ids))

    def execute_three_tier(self, signal: ParsedSignal, message_id: int) -> Dict:
        try:
            tier_units, usd_sgd_rate, expected_loss = self.compute_units(signal)
            if expected_loss > 30.0 and (self.store.get_trade_count() if self.store else 0) < 10:
                raise RuntimeError(f"Expected loss too high: {expected_loss:.2f}")

            entry_prices = self._entry_prices(signal)
            total_units = sum(tier_units)
            entry_mid = (signal.entry_low + signal.entry_high) / 2.0
            signed = 1 if signal.direction == "BUY" else -1
            responses = []
            for idx, (units, entry_price) in enumerate(zip(tier_units, entry_prices), start=1):
                if units <= 0:
                    continue
                response = self.oanda.create_limit_order(
                    instrument=signal.symbol,
                    units=signed * units,
                    price=entry_price,
                    stop_loss=signal.stop_loss,
                    client_tag=f"qv3-{message_id}-tier{idx}",
                )
                responses.append(response)

            trade_ids = self._extract_trade_ids(responses)

            return {
                "message_id": message_id,
                "symbol": signal.symbol,
                "direction": signal.direction,
                "entry_price": entry_mid,
                "entry_prices": entry_prices,
                "original_units": total_units,
                "remaining_units": total_units,
                "stop_loss": signal.stop_loss,
                "tp_levels": signal.tp_levels,
                "tp_levels_hit": [],
                "runner_active": False,
                "runner_steps_hit": 0,
                "trailing_sl": signal.stop_loss,
                "sl_pips": abs(entry_mid - signal.stop_loss) * 100.0,
                "risk_sgd": expected_loss,
                "usd_sgd_rate": usd_sgd_rate,
                "trade_ids": trade_ids,
                "orders": responses,
            }
        except Exception:
            raise

    def execute_signal(self, signal: Union[ParsedSignal, Dict], message_id: int) -> Dict:
        if isinstance(signal, ParsedSignal):
            return self.execute_three_tier(signal, message_id)
        parsed = ParsedSignal(
            symbol=signal["symbol"],
            direction=signal["direction"],
            entry_low=float(signal["entry_low"]),
            entry_high=float(signal["entry_high"]),
            stop_loss=float(signal["stop_loss"]),
            tp_levels=[float(x) for x in signal.get("tp_levels", [])],
        )
        return self.execute_three_tier(parsed, message_id)
