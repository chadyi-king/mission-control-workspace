from dataclasses import dataclass

from oanda_client import OandaClient
from redis_backbone import RedisState


@dataclass
class RiskBreakdown:
    risk_total_sgd: float
    risk_per_tier_sgd: float
    mode: str


class RiskManager:
    def __init__(self, oanda: OandaClient, redis_state: RedisState):
        self.oanda = oanda
        self.redis_state = redis_state

    def resolve_risk(self) -> RiskBreakdown:
        try:
            completed = self.redis_state.get_trade_count()
            if completed < 10:
                return RiskBreakdown(risk_total_sgd=30.0, risk_per_tier_sgd=10.0, mode="phase1_fixed")

            account = self.oanda.get_account_summary()
            equity_sgd = float(account.get("NAV", account.get("balance", 0)))
            risk_total_sgd = equity_sgd * 0.02
            return RiskBreakdown(
                risk_total_sgd=risk_total_sgd,
                risk_per_tier_sgd=(risk_total_sgd / 3.0),
                mode="phase2_equity_pct",
            )
        except Exception:
            raise

    def calculate_units_and_explain(self, symbol: str, entry_price: float, stop_loss: float, risk_per_tier_sgd: float) -> dict:
        try:
            account_ccy_loss_per_unit = self.oanda.get_account_ccy_loss_per_unit(symbol, entry_price, stop_loss)
            units = int(max(risk_per_tier_sgd / account_ccy_loss_per_unit, 1))
            expected_loss_sgd = units * account_ccy_loss_per_unit
            if expected_loss_sgd > risk_per_tier_sgd:
                raise RuntimeError(
                    f"expected_loss_sgd={expected_loss_sgd:.4f} exceeds risk_per_tier_sgd={risk_per_tier_sgd:.4f}"
                )

            pip_size = self.oanda.get_pip_size(symbol)
            price_distance = abs(entry_price - stop_loss)
            pip_distance = price_distance / pip_size if pip_size > 0 else 0.0

            return {
                "units": units,
                "expected_loss_sgd": expected_loss_sgd,
                "account_ccy_loss_per_unit": account_ccy_loss_per_unit,
                "price_distance": price_distance,
                "pip_distance": pip_distance,
                "pip_size": pip_size,
            }
        except Exception:
            raise
