import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ParsedSignal:
    symbol: str
    direction: str
    entry_low: float
    entry_high: float
    stop_loss: float
    tp_levels: List[float]


class SignalParser:
    SYMBOL_RE = re.compile(r"\bXAUUSD\b", re.IGNORECASE)
    DIR_RE = re.compile(r"\b(BUY|SELL)\b", re.IGNORECASE)
    RANGE_RE = re.compile(r"(?:RANGE|ENTRY|ZONE)?\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*[-~]\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
    SL_RE = re.compile(r"\bSL\b\s*[:\-]?\s*(\d+(?:\.\d+)?)", re.IGNORECASE)
    TP_BLOCK_RE = re.compile(r"\bTP\b\s*[:\-]?\s*([\d./\s]+)", re.IGNORECASE)
    TP_NUMBER_RE = re.compile(r"\bTP\d*\b\s*[:\-]?\s*(\d+(?:\.\d+)?)", re.IGNORECASE)

    def parse(self, text: str) -> Optional[ParsedSignal]:
        try:
            normalized = text.replace("\n", " ")
            if not self.SYMBOL_RE.search(normalized):
                return None
            direction_match = self.DIR_RE.search(normalized)
            range_match = self.RANGE_RE.search(normalized)
            sl_match = self.SL_RE.search(normalized)
            if not direction_match or not range_match or not sl_match:
                return None

            low = float(range_match.group(1))
            high = float(range_match.group(2))
            entry_low, entry_high = sorted((low, high))
            stop_loss = float(sl_match.group(1))

            tps = [float(m.group(1)) for m in self.TP_NUMBER_RE.finditer(normalized)]
            block = self.TP_BLOCK_RE.search(normalized)
            if block:
                tps.extend(float(v) for v in re.findall(r"\d+(?:\.\d+)?", block.group(1)))
            tps = list(dict.fromkeys(tps))

            return ParsedSignal(
                symbol="XAUUSD",
                direction=direction_match.group(1).upper(),
                entry_low=entry_low,
                entry_high=entry_high,
                stop_loss=stop_loss,
                tp_levels=tps,
            )
        except Exception:
            return None
