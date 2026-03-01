from collections import Counter
from typing import Dict, Iterable

from signal_parser import SignalParser


class PatternLearner:
    def __init__(self, parser: SignalParser):
        self.parser = parser

    def learn(self, messages: Iterable[str]) -> Dict:
        symbols = Counter()
        tp_tokens = Counter()
        separators = Counter()

        for text in messages:
            parsed = self.parser.parse(text, message_id=0)
            if parsed:
                symbols[parsed.symbol] += 1
            if "TP1" in text.upper():
                tp_tokens["TP#"] += 1
            if "TP " in text.upper():
                tp_tokens["TP space"] += 1
            if "-" in text:
                separators["-"] += 1
            if "~" in text:
                separators["~"] += 1

        return {
            "common_symbols": symbols.most_common(10),
            "tp_styles": tp_tokens.most_common(5),
            "range_separators": separators.most_common(5),
        }
