from dataclasses import dataclass
from typing import Optional

from redis_backbone import RedisBackbone


@dataclass
class RiskDecision:
    risk_sgd: float
    mode: str


class RiskManager:
    def __init__(self, store: RedisBackbone):
        self.store = store

    def calculate(self, equity: Optional[float]) -> RiskDecision:
        trade_count = self.store.get_trade_count()

        if trade_count < 10:
            risk = 30.0
            mode = "fixed_30_sgd_first_10"
        else:
            if equity is None:
                raise RuntimeError("Equity is required for 2% risk sizing")
            risk = float(equity) * 0.02
            mode = "equity_2pct"

        if hasattr(self.store, "set_risk_mode"):
            self.store.set_risk_mode(mode)
        return RiskDecision(risk_sgd=risk, mode=mode)

    def tier_risks(self, equity: Optional[float]) -> list[float]:
        decision = self.calculate(equity)
        total = decision.risk_sgd
        return [total * 0.33, total * 0.33, total * 0.34]
