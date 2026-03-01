import unittest

from trade_manager import TradeManager
from signal_parser import ParsedSignal


class FakeOanda:
    def __init__(self):
        self.calls = []

    def create_limit_order(self, instrument, units, price, stop_loss, client_tag):
        self.calls.append(
            {
                "type": "LIMIT",
                "instrument": instrument,
                "units": units,
                "price": price,
                "stop_loss": stop_loss,
                "client_tag": client_tag,
            }
        )
        return {
            "orderFillTransaction": {"tradeOpened": {"tradeID": f"T{len(self.calls)}"}},
            "orderCreateTransaction": {"id": f"O{len(self.calls)}"},
        }

    def get_account_summary(self):
        return {"NAV": "10000.00", "balance": "10000.00"}

    def get_price(self, instrument):
        if instrument == "USD_SGD":
            return 1.35
        if instrument == "SGD_USD":
            return 1.0 / 1.35
        return 1.0


class FakeRiskManager:
    def tier_risks(self, equity):
        return [10.0, 10.0, 10.0]


class TestTradeManager(unittest.TestCase):
    def test_execute_three_tier_extracts_trade_ids(self):
        oanda = FakeOanda()
        mgr = TradeManager(oanda, risk_manager=FakeRiskManager())
        signal = ParsedSignal(
            symbol="XAUUSD",
            direction="BUY",
            entry_low=4973.0,
            entry_high=4978.0,
            stop_loss=4974.5,
            tp_levels=[5000.0, 5020.0, 5030.0],
        )
        result = mgr.execute_three_tier(signal, message_id=123)
        self.assertEqual(len(oanda.calls), 3)
        self.assertTrue(all(c["type"] == "LIMIT" for c in oanda.calls))
        for tid in ("T1", "T2", "T3"):
            self.assertIn(tid, result["trade_ids"])


if __name__ == "__main__":
    unittest.main()
