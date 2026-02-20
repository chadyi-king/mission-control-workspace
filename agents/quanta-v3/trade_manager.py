from typing import Dict, List, Tuple

from oanda_client import OandaClient
from signal_parser import ParsedSignal


class TradeManager:
    def __init__(self, oanda: OandaClient):
        self.oanda = oanda

    def compute_units(self, signal: ParsedSignal) -> Tuple[int, float, float]:
        try:
            sl_distance = abs(((signal.entry_low + signal.entry_high) / 2) - signal.stop_loss)
            sl_pips = sl_distance * 100
            pip_value_per_unit = 0.01
            units = int(20 / (pip_value_per_unit * sl_pips)) if sl_pips > 0 else 0
            expected_loss = units * pip_value_per_unit * sl_pips
            return max(units, 0), sl_pips, expected_loss
        except Exception:
            raise

    def _tier_units(self, total_units: int) -> List[int]:
        try:
            first = int(total_units * 0.33)
            second = int(total_units * 0.33)
            third = total_units - first - second
            return [first, second, third]
        except Exception:
            raise

    def execute_three_tier(self, signal: ParsedSignal, message_id: int) -> Dict:
        try:
            total_units, sl_pips, expected_loss = self.compute_units(signal)
            if total_units <= 0:
                raise RuntimeError("Computed units <= 0")
            if expected_loss > 30:
                raise RuntimeError(f"Expected loss too high: {expected_loss:.2f}")

            entry_high = signal.entry_high
            entry_mid = (signal.entry_low + signal.entry_high) / 2
            entry_low = signal.entry_low
            _ = [entry_high, entry_mid, entry_low]

            tiers = self._tier_units(total_units)
            signed = 1 if signal.direction == "BUY" else -1
            responses = []
            for idx, units in enumerate(tiers, start=1):
                if units <= 0:
                    continue
                response = self.oanda.create_market_order(
                    instrument=signal.symbol,
                    units=signed * units,
                    stop_loss=signal.stop_loss,
                    client_tag=f"qv3-{message_id}-tier{idx}",
                )
                responses.append(response)

            return {
                "message_id": message_id,
                "symbol": signal.symbol,
                "direction": signal.direction,
                "entry_price": entry_mid,
                "original_units": total_units,
                "remaining_units": total_units,
                "stop_loss": signal.stop_loss,
                "tp_levels_hit": [],
                "runner_active": False,
                "runner_steps_hit": 0,
                "trailing_sl": signal.stop_loss,
                "sl_pips": sl_pips,
                "orders": responses,
            }
        except Exception:
            raise
