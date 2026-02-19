from typing import Dict, List

from config import CHANNEL_PIP_SIZE, channel_pips_to_price
from oanda_client import OandaClient
from redis_backbone import RedisState
from risk_manager import RiskManager
from signal_parser import ParsedSignal


class TradeManager:
    def __init__(self, oanda: OandaClient, state: RedisState):
        self.oanda = oanda
        self.state = state
        self.risk_manager = RiskManager(oanda, state)

    def _entry_prices(self, signal: ParsedSignal) -> List[float]:
        try:
            low, high = signal.entry_low, signal.entry_high
            mid = (low + high) / 2
            if signal.direction == "BUY":
                return [low, mid, high]
            return [high, mid, low]
        except Exception:
            raise

    def execute_signal(self, signal: ParsedSignal, message_id: int) -> Dict:
        try:
            risk = self.risk_manager.resolve_risk()
            entries = self._entry_prices(signal)
            side = 1 if signal.direction == "BUY" else -1

            anchor_entry = min(entries) if signal.direction == "BUY" else max(entries)
            worst_entry = max(entries) if signal.direction == "BUY" else min(entries)
            worst_distance = abs(worst_entry - signal.stop_loss)
            if worst_distance <= 0:
                raise RuntimeError("invalid worst-distance for risk")

            pip_size = self.oanda.get_pip_size(signal.symbol) or 0.0001

            tp_price_targets = {
                "tp1": anchor_entry + channel_pips_to_price(signal.symbol, 20) if signal.direction == "BUY" else anchor_entry - channel_pips_to_price(signal.symbol, 20),
                "tp2": anchor_entry + channel_pips_to_price(signal.symbol, 40) if signal.direction == "BUY" else anchor_entry - channel_pips_to_price(signal.symbol, 40),
                "tp3": anchor_entry + channel_pips_to_price(signal.symbol, 60) if signal.direction == "BUY" else anchor_entry - channel_pips_to_price(signal.symbol, 60),
                "tp4": anchor_entry + channel_pips_to_price(signal.symbol, 80) if signal.direction == "BUY" else anchor_entry - channel_pips_to_price(signal.symbol, 80),
                "tp5": anchor_entry + channel_pips_to_price(signal.symbol, 100) if signal.direction == "BUY" else anchor_entry - channel_pips_to_price(signal.symbol, 100),
            }
            tp_pip_targets = {k: abs(v - anchor_entry) / pip_size for k, v in tp_price_targets.items()}

            tier_orders: List[Dict] = []
            total_units = 0
            total_expected_loss_sgd = 0.0

            for idx, entry_price in enumerate(entries, start=1):
                sizing = self.risk_manager.calculate_units_and_explain(
                    symbol=signal.symbol,
                    entry_price=entry_price,
                    stop_loss=signal.stop_loss,
                    risk_per_tier_sgd=risk.risk_per_tier_sgd,
                )
                units = int(sizing["units"])
                placed = self.oanda.create_limit_order(
                    instrument=signal.symbol,
                    units=side * units,
                    price=entry_price,
                    stop_loss=signal.stop_loss,
                    client_tag=f"qv3-{signal.signal_id}-tier{idx}",
                )
                order_id = str((placed.get("orderCreateTransaction") or {}).get("id", ""))
                tier_orders.append(
                    {
                        "tier": idx,
                        "entry": entry_price,
                        "units": units,
                        "risk_sgd": risk.risk_per_tier_sgd,
                        "expected_loss_sgd": sizing["expected_loss_sgd"],
                        "order_id": order_id,
                    }
                )
                total_units += units
                total_expected_loss_sgd += float(sizing["expected_loss_sgd"])

            signal_state = {
                "signal_id": signal.signal_id,
                "symbol": signal.symbol,
                "direction": signal.direction,
                "tier_orders": tier_orders,
                "original_position_size": total_units,
                "original_total_units": total_units,
                "remaining_position_size": total_units,
                "remaining_total_units": total_units,
                "first_entry_price": anchor_entry,
                "runner_mode_active": False,
                "runner_active": False,
                "runner_trigger_price": 0.0,
                "runner_next_trigger": 200,
                "current_trailing_sl": signal.stop_loss,
                "stop_loss": signal.stop_loss,
                "tp_levels_hit": [],
                "tp1_done": False,
                "tp2_done": False,
                "tp3_done": False,
                "tp4_done": False,
                "tp5_done": False,
                "status": "open",
                "message_id": message_id,
                "risk_mode": risk.mode,
                "tp_price_targets": tp_price_targets,
                "tp_pip_targets": tp_pip_targets,
                "stored_pip_distance": 0.0,
                "explain": {
                    "channel_pip_distance": worst_distance / CHANNEL_PIP_SIZE.get(signal.symbol.upper(), 0.0001),
                    "actual_price_distance": worst_distance,
                    "pip_size": pip_size,
                    "total_sgd_risk": total_expected_loss_sgd,
                },
            }
            self.state.save_signal_state(signal.signal_id, signal_state)
            self.state.increment_trade_count()
            return signal_state
        except Exception:
            raise
