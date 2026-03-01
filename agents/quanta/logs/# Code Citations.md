# Code Citations

## License: LGPL-2.1
https://github.com/mnesarco/fcapi/blob/8434ea5371a926e1eb87acb5a837ab7d40afe749/fpo.py

```
Got it. I'm wiring the full strategy into the live execution loop now, gold-first, with FX as a placeholder for later.

````python
# filepath: /home/chad-yi/mission-control-workspace/agents/quanta-v3/executor.py
import math
import time
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional

logger = logging.getLogger("quanta-v3")

# ─── Pip config per symbol ────────────────────────────────────────────────────
# channel_pip_to_price: how much $price move = 1 channel pip
# Add FX symbols later once confirmed
SYMBOL_CONFIG = {
    "XAU_USD": {
        "channel_pip_to_price": 0.10,   # 1 ch-pip = $0.10
    },
    # FX placeholder — confirm before enabling live
    "EUR_USD": {
        "channel_pip_to_price": 0.0001,
    },
    "GBP_USD": {
        "channel_pip_to_price": 0.0001,
    },
}

# ─── Strategy constants ───────────────────────────────────────────────────────
TP_LEVELS_CHANNEL_PIPS    = [20, 40, 60, 80, 100]
TP_PARTIAL_PCT_FIXED      = 0.10   # 10% of original units at each TP1-5
RUNNER_INTERVAL_PIPS      = 100    # runner fires every 100 ch-pips after TP5
RUNNER_PARTIAL_PCT        = 0.10   # 10% of REMAINING units
RUNNER_SL_TRAIL_PIPS      = 100    # SL = milestone - 100 ch-pips
FIXED_RISK_SGD            = 30.0
FIXED_RISK_TRADE_COUNT    = 10
EQUITY_RISK_PCT           = 0.02   # 2% after first 10 trades


# ─── Helpers ──────────────────────────────────────────────────────────────────
def ch_pips_to_price(symbol: str, pips: float) -> float:
    cfg = SYMBOL_CONFIG.get(symbol, {"channel_pip_to_price": 0.0001})
    return pips * cfg["channel_pip_to_price"]


def price_to_ch_pips(symbol: str, price_move: float) -> float:
    cfg = SYMBOL_CONFIG.get(symbol, {"channel_pip_to_price": 0.0001})
    return price_move / cfg["channel_pip_to_price"]


def calculate_units(symbol: str, entry: float, sl: float, risk_sgd: float) -> int:
    sl_distance = abs(entry - sl)
    if sl_distance == 0:
        raise ValueError(f"SL distance is zero for {symbol}")
    units = risk_sgd / sl_distance
    return max(1, int(units))


def get_risk_sgd(trade_count: int, account_balance_sgd: float) -> float:
    if trade_count < FIXED_RISK_TRADE_COUNT:
        return FIXED_RISK_SGD
    return account_balance_sgd * EQUITY_RISK_PCT


# ─── Trade state ──────────────────────────────────────────────────────────────
@dataclass
class TradeState:
    trade_id:        
```


## License: LGPL-2.1
https://github.com/mnesarco/fcapi/blob/8434ea5371a926e1eb87acb5a837ab7d40afe749/fpo.py

```
Got it. I'm wiring the full strategy into the live execution loop now, gold-first, with FX as a placeholder for later.

````python
# filepath: /home/chad-yi/mission-control-workspace/agents/quanta-v3/executor.py
import math
import time
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional

logger = logging.getLogger("quanta-v3")

# ─── Pip config per symbol ────────────────────────────────────────────────────
# channel_pip_to_price: how much $price move = 1 channel pip
# Add FX symbols later once confirmed
SYMBOL_CONFIG = {
    "XAU_USD": {
        "channel_pip_to_price": 0.10,   # 1 ch-pip = $0.10
    },
    # FX placeholder — confirm before enabling live
    "EUR_USD": {
        "channel_pip_to_price": 0.0001,
    },
    "GBP_USD": {
        "channel_pip_to_price": 0.0001,
    },
}

# ─── Strategy constants ───────────────────────────────────────────────────────
TP_LEVELS_CHANNEL_PIPS    = [20, 40, 60, 80, 100]
TP_PARTIAL_PCT_FIXED      = 0.10   # 10% of original units at each TP1-5
RUNNER_INTERVAL_PIPS      = 100    # runner fires every 100 ch-pips after TP5
RUNNER_PARTIAL_PCT        = 0.10   # 10% of REMAINING units
RUNNER_SL_TRAIL_PIPS      = 100    # SL = milestone - 100 ch-pips
FIXED_RISK_SGD            = 30.0
FIXED_RISK_TRADE_COUNT    = 10
EQUITY_RISK_PCT           = 0.02   # 2% after first 10 trades


# ─── Helpers ──────────────────────────────────────────────────────────────────
def ch_pips_to_price(symbol: str, pips: float) -> float:
    cfg = SYMBOL_CONFIG.get(symbol, {"channel_pip_to_price": 0.0001})
    return pips * cfg["channel_pip_to_price"]


def price_to_ch_pips(symbol: str, price_move: float) -> float:
    cfg = SYMBOL_CONFIG.get(symbol, {"channel_pip_to_price": 0.0001})
    return price_move / cfg["channel_pip_to_price"]


def calculate_units(symbol: str, entry: float, sl: float, risk_sgd: float) -> int:
    sl_distance = abs(entry - sl)
    if sl_distance == 0:
        raise ValueError(f"SL distance is zero for {symbol}")
    units = risk_sgd / sl_distance
    return max(1, int(units))


def get_risk_sgd(trade_count: int, account_balance_sgd: float) -> float:
    if trade_count < FIXED_RISK_TRADE_COUNT:
        return FIXED_RISK_SGD
    return account_balance_sgd * EQUITY_RISK_PCT


# ─── Trade state ──────────────────────────────────────────────────────────────
@dataclass
class TradeState:
    trade_id:        
```


## License: LGPL-2.1
https://github.com/mnesarco/fcapi/blob/8434ea5371a926e1eb87acb5a837ab7d40afe749/fpo.py

```
Got it. I'm wiring the full strategy into the live execution loop now, gold-first, with FX as a placeholder for later.

````python
# filepath: /home/chad-yi/mission-control-workspace/agents/quanta-v3/executor.py
import math
import time
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional

logger = logging.getLogger("quanta-v3")

# ─── Pip config per symbol ────────────────────────────────────────────────────
# channel_pip_to_price: how much $price move = 1 channel pip
# Add FX symbols later once confirmed
SYMBOL_CONFIG = {
    "XAU_USD": {
        "channel_pip_to_price": 0.10,   # 1 ch-pip = $0.10
    },
    # FX placeholder — confirm before enabling live
    "EUR_USD": {
        "channel_pip_to_price": 0.0001,
    },
    "GBP_USD": {
        "channel_pip_to_price": 0.0001,
    },
}

# ─── Strategy constants ───────────────────────────────────────────────────────
TP_LEVELS_CHANNEL_PIPS    = [20, 40, 60, 80, 100]
TP_PARTIAL_PCT_FIXED      = 0.10   # 10% of original units at each TP1-5
RUNNER_INTERVAL_PIPS      = 100    # runner fires every 100 ch-pips after TP5
RUNNER_PARTIAL_PCT        = 0.10   # 10% of REMAINING units
RUNNER_SL_TRAIL_PIPS      = 100    # SL = milestone - 100 ch-pips
FIXED_RISK_SGD            = 30.0
FIXED_RISK_TRADE_COUNT    = 10
EQUITY_RISK_PCT           = 0.02   # 2% after first 10 trades


# ─── Helpers ──────────────────────────────────────────────────────────────────
def ch_pips_to_price(symbol: str, pips: float) -> float:
    cfg = SYMBOL_CONFIG.get(symbol, {"channel_pip_to_price": 0.0001})
    return pips * cfg["channel_pip_to_price"]


def price_to_ch_pips(symbol: str, price_move: float) -> float:
    cfg = SYMBOL_CONFIG.get(symbol, {"channel_pip_to_price": 0.0001})
    return price_move / cfg["channel_pip_to_price"]


def calculate_units(symbol: str, entry: float, sl: float, risk_sgd: float) -> int:
    sl_distance = abs(entry - sl)
    if sl_distance == 0:
        raise ValueError(f"SL distance is zero for {symbol}")
    units = risk_sgd / sl_distance
    return max(1, int(units))


def get_risk_sgd(trade_count: int, account_balance_sgd: float) -> float:
    if trade_count < FIXED_RISK_TRADE_COUNT:
        return FIXED_RISK_SGD
    return account_balance_sgd * EQUITY_RISK_PCT


# ─── Trade state ──────────────────────────────────────────────────────────────
@dataclass
class TradeState:
    trade_id:        
```

