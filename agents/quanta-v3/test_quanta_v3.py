import unittest

from signal_parser import SignalParser


class TestParser(unittest.TestCase):
    def test_valid_signal(self):
        p = SignalParser()
        s = p.parse("🟢XAUUSD🟢 BUY RANGE: 4973-4978 SL 4968 TP: 5000/5020/5030")
        self.assertIsNotNone(s)
        self.assertEqual(s.symbol, "XAUUSD")
        self.assertEqual(s.tp_levels, [5000.0, 5020.0, 5030.0])

    def test_reject_non_xau(self):
        p = SignalParser()
        self.assertIsNone(p.parse("EURUSD BUY RANGE: 1.0900-1.0910 SL 1.0880"))


if __name__ == "__main__":
    unittest.main()
