from dataclasses import dataclass

from redis_backbone import RedisBackbone


@dataclass
class RiskDecision:
    risk_sgd: float
    mode: str


class RiskManager:
    def __init__(self, store: RedisBackbone):
        self.store = store

    def calculate(self, equity: float) -> RiskDecision:
        trade_count = self.store.get_trade_count()
        baseline = self.store.get_baseline_equity()

        if baseline is None:
            baseline = equity
            self.store.set_baseline_equity(baseline)

        if trade_count < 20:
            risk = 20.0
            mode = "fixed_20"
        else:
            growth = (equity - baseline) / baseline if baseline else 0
            pct = 0.02 if growth >= 0.10 else 0.01
            risk = equity * pct
            mode = f"equity_{int(pct*100)}pct"

        if risk > 30:
            raise RuntimeError(f"Risk {risk:.2f} SGD exceeds hard cap of 30 SGD")

        self.store.set_risk_mode(mode)
        return RiskDecision(risk_sgd=risk, mode=mode)
