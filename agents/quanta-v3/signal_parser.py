import hashlib
import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ParsedSignal:
    signal_id: str
    symbol: str
    direction: str
    entry_low: float
    entry_high: float
    stop_loss: float
    tp_list: List[float]


class SignalParser:
    SYMBOL_RE = re.compile(r"\b([A-Z]{6})\b")

    def _clean(self, text: str) -> str:
        try:
            out = text.upper().replace("\n", " ")
            out = re.sub(r"[^A-Z0-9./\-:\s]", " ", out)
            out = re.sub(r"\s+", " ", out).strip()
            return out
        except Exception:
            return text.upper()

    def parse(self, raw_text: str, message_id: int) -> Optional[ParsedSignal]:
        try:
            text = self._clean(raw_text)
            direction = "BUY" if "BUY" in text else "SELL" if "SELL" in text else None
            if not direction:
                return None

            range_word = any(k in text for k in ["RANGE", "ENTRY", "ZONE"])
            range_m = re.search(r"(\d+(?:\.\d+)?)\s*[-~]\s*(\d+(?:\.\d+)?)", text)
            if not range_word or not range_m:
                return None

            sl_m = re.search(r"\bSL\b\s*[:\-]?\s*(\d+(?:\.\d+)?)", text)
            if not sl_m:
                return None

            tp_list = [float(x) for x in re.findall(r"TP\d*\s*[:\-]?\s*(\d+(?:\.\d+)?)", text)]
            if "TP" in text:
                block = re.search(r"TP\s*[:\-]?\s*([0-9./\s]+)", text)
                if block:
                    tp_list.extend(float(x) for x in re.findall(r"\d+(?:\.\d+)?", block.group(1)))
            tp_list = sorted(list(dict.fromkeys(tp_list)))

            symbol_m = self.SYMBOL_RE.search(text)
            symbol = symbol_m.group(1) if symbol_m else "XAUUSD"
            low, high = sorted((float(range_m.group(1)), float(range_m.group(2))))
            sl = float(sl_m.group(1))

            sid_seed = f"{message_id}|{symbol}|{direction}|{low}|{high}|{sl}|{','.join(map(str,tp_list))}|{text}"
            sid = hashlib.sha256(sid_seed.encode()).hexdigest()
            return ParsedSignal(sid, symbol, direction, low, high, sl, tp_list)
        except Exception:
            return None
