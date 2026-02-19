import unittest

from config import channel_pips_to_price
from risk_manager import RiskManager
from signal_parser import SignalParser
from trade_manager import TradeManager


class DummyRedisState:
    def __init__(self):
        self.trade_count = 0
        self.saved = {}

    def get_trade_count(self):
        return self.trade_count

    def increment_trade_count(self):
        self.trade_count += 1
        return self.trade_count

    def save_signal_state(self, sid, payload):
        self.saved[sid] = payload


class DummyOanda:
    def get_account_summary(self):
        return {"balance": "1000", "NAV": "1000"}

    def get_instrument_spec(self, instrument):
        if instrument == "XAUUSD":
            return {"pip_size": 0.01, "contract_size": 100.0, "display_precision": 2}
        return {"pip_size": 0.0001, "contract_size": 100000.0, "display_precision": 5}

    def get_pip_size(self, symbol):
        return 0.01 if symbol == "XAUUSD" else 0.0001

    def get_account_ccy_loss_per_unit(self, symbol, entry, stop):
        return abs(entry - stop)

    def get_sgd_loss_per_unit(self, symbol, entry, stop):
        return self.get_account_ccy_loss_per_unit(symbol, entry, stop)

    def create_limit_order(self, instrument, units, price, stop_loss, client_tag):
        return {"orderCreateTransaction": {"id": f"{client_tag}-id"}}


class ParserTests(unittest.TestCase):
    def test_signal_with_tp(self):
        p = SignalParser()
        s = p.parse("🟢XAUUSD🟢 BUY RANGE: 4926-4932 SL 4921 TP:4958/4968/4988/4998", 101)
        self.assertIsNotNone(s)
        self.assertEqual(s.symbol, "XAUUSD")
        self.assertEqual(s.direction, "BUY")
        self.assertEqual(len(s.tp_list), 4)

    def test_signal_without_tp_is_valid(self):
        p = SignalParser()
        s = p.parse("xauusd sell range 4937.5-4943 sl 4948", 102)
        self.assertIsNotNone(s)
        self.assertEqual(s.direction, "SELL")


class RiskTradeTests(unittest.TestCase):
    def test_phase1_risk(self):
        rs = DummyRedisState()
        rm = RiskManager(DummyOanda(), rs)
        r = rm.resolve_risk()
        self.assertEqual(r.risk_total_sgd, 30.0)
        self.assertEqual(r.risk_per_tier_sgd, 10.0)

    def test_channel_pip_conversion(self):
        self.assertEqual(channel_pips_to_price("XAUUSD", 20), 2.0)
        self.assertEqual(channel_pips_to_price("USDJPY", 20), 0.2)
        self.assertEqual(channel_pips_to_price("BRENT", 100), 1.0)

    def test_price_distance_sizing(self):
        rs = DummyRedisState()
        rm = RiskManager(DummyOanda(), rs)
        out = rm.calculate_units_and_explain("XAUUSD", 4930.0, 4929.0, 10.0)
        self.assertGreater(out["units"], 0)
        self.assertAlmostEqual(out["price_distance"], 1.0)

    def test_trade_state_fields(self):
        rs = DummyRedisState()
        tm = TradeManager(DummyOanda(), rs)
        s = SignalParser().parse("XAUUSD BUY RANGE: 4926-4932 SL 4925 TP:4958/4968", 99)
        out = tm.execute_signal(s, 99)
        for k in [
            "signal_id",
            "tier_orders",
            "original_position_size",
            "remaining_position_size",
            "first_entry_price",
            "runner_mode_active",
            "runner_trigger_price",
            "current_trailing_sl",
            "tp_price_targets",
            "tp_pip_targets",
            "stored_pip_distance",
            "explain",
        ]:
            self.assertIn(k, out)


if __name__ == "__main__":
    unittest.main()
