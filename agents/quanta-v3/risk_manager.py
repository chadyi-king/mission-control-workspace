from dataclasses import dataclass

from oanda_client import OandaClient
from redis_backbone import RedisState


@dataclass
class RiskBreakdown:
    risk_total: float
    risk_per_tier: float
    mode: str


class RiskManager:
    def __init__(self, oanda: OandaClient, redis_state: RedisState):
        self.oanda = oanda
        self.redis_state = redis_state

    def resolve_risk(self) -> RiskBreakdown:
        try:
            completed = self.redis_state.get_trade_count()
            if completed < 10:
                risk_total = 30.0
                return RiskBreakdown(risk_total=risk_total, risk_per_tier=10.0, mode="phase1_fixed")

            account = self.oanda.get_account_summary()
            equity = float(account.get("NAV", account.get("balance", 0)))
            risk_percent = 0.02
            risk_total = equity * risk_percent
            return RiskBreakdown(risk_total=risk_total, risk_per_tier=(risk_total / 3.0), mode="phase2_equity_pct")
        except Exception:
            raise

    def calculate_units_and_explain(self, symbol: str, entry_price: float, stop_loss: float, risk_per_tier: float) -> dict:
        try:
            price_distance = abs(entry_price - stop_loss)
            if price_distance <= 0:
                raise RuntimeError("price_distance must be > 0")

            usd_loss_per_unit = self.oanda.get_usd_loss_per_unit(symbol, entry_price, stop_loss)
            units = int(max(risk_per_tier / usd_loss_per_unit, 1))
            expected_loss = units * usd_loss_per_unit
            if expected_loss > risk_per_tier:
                raise RuntimeError(
                    f"expected_loss={expected_loss:.4f} exceeds risk_per_tier={risk_per_tier:.4f}"
                )

            spec = self.oanda.get_instrument_spec(symbol)
            broker_pip_distance = price_distance / float(spec.get("pip_size", 0.0001))

            return {
                "units": units,
                "expected_loss_usd": expected_loss,
                "price_distance": price_distance,
                "usd_loss_per_unit": usd_loss_per_unit,
                "broker_pip_distance": broker_pip_distance,
            }
        except Exception:
            raise
