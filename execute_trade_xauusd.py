#!/usr/bin/env python3
"""Execute XAUUSD BUY trade via OANDA"""
import requests
import json
from datetime import datetime

# OANDA credentials
ACCOUNT_ID = "001-003-8520002-001"
API_KEY = "8d4ff0fbea2b109c515a956784596208-be028efcd5faae816357345ff32c3bac"
BASE_URL = "https://api-fxtrade.oanda.com/v3"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Signal details
PAIR = "XAU_USD"
ENTRY_LOW = 4970.0
ENTRY_HIGH = 4976.0
SL = 4966.0
TPS = [5000.0, 5010.0, 5020.0]

# Risk parameters
RISK_USD = 20.0
ENTRY_MID = (ENTRY_LOW + ENTRY_HIGH) / 2  # 4973.0
RISK_PIPS = ENTRY_MID - SL  # 7.0 pips

# Calculate position size for $20 risk
# XAUUSD: 1 pip = $0.01 per unit, so 1 lot (100 units) = $1 per pip
POSITION_SIZE = RISK_USD / RISK_PIPS  # ~2.85 lots total

# 3-Tier DCA
TIER_1_SIZE = round(POSITION_SIZE * 0.33, 2)  # 0.94 lots @ 4976
TIER_2_SIZE = round(POSITION_SIZE * 0.33, 2)  # 0.94 lots @ 4973
TIER_3_SIZE = round(POSITION_SIZE * 0.34, 2)  # 0.97 lots @ 4970

print(f"🚀 EXECUTING XAUUSD BUY")
print(f"Entry Range: {ENTRY_LOW} - {ENTRY_HIGH}")
print(f"SL: {SL}")
print(f"TPs: {TPS}")
print(f"Risk: ${RISK_USD}")
print(f"Position Size: {POSITION_SIZE} lots total")
print(f"")
print(f"Tier 1: {TIER_1_SIZE} lots @ {ENTRY_HIGH}")
print(f"Tier 2: {TIER_2_SIZE} lots @ {ENTRY_MID}")
print(f"Tier 3: {TIER_3_SIZE} lots @ {ENTRY_LOW}")

# Create orders (pending - will trigger when price hits)
orders = []

# Tier 1 - High of range
order1 = {
    "order": {
        "type": "LIMIT",
        "instrument": PAIR,
        "units": str(int(TIER_1_SIZE * 100)),  # Convert to units
        "price": str(ENTRY_HIGH),
        "stopLossOnFill": {
            "price": str(SL)
        },
        "takeProfitOnFill": {
            "price": str(TPS[2])  # TP3 for runner
        },
        "timeInForce": "GTC",
        "positionFill": "DEFAULT"
    }
}
orders.append(("Tier 1 (High)", order1))

# Tier 2 - Mid of range
order2 = {
    "order": {
        "type": "LIMIT",
        "instrument": PAIR,
        "units": str(int(TIER_2_SIZE * 100)),
        "price": str(ENTRY_MID),
        "stopLossOnFill": {
            "price": str(SL)
        },
        "takeProfitOnFill": {
            "price": str(TPS[2])
        },
        "timeInForce": "GTC",
        "positionFill": "DEFAULT"
    }
}
orders.append(("Tier 2 (Mid)", order2))

# Tier 3 - Low of range
order3 = {
    "order": {
        "type": "LIMIT",
        "instrument": PAIR,
        "units": str(int(TIER_3_SIZE * 100)),
        "price": str(ENTRY_LOW),
        "stopLossOnFill": {
            "price": str(SL)
        },
        "takeProfitOnFill": {
            "price": str(TPS[2])
        },
        "timeInForce": "GTC",
        "positionFill": "DEFAULT"
    }
}
orders.append(("Tier 3 (Low)", order3))

# Execute orders
results = []
for name, order in orders:
    try:
        response = requests.post(
            f"{BASE_URL}/accounts/{ACCOUNT_ID}/orders",
            headers=headers,
            json=order
        )
        if response.status_code == 201:
            results.append(f"✅ {name}: Order placed successfully")
            print(f"✅ {name}: Order placed")
        else:
            results.append(f"❌ {name}: {response.status_code} - {response.text}")
            print(f"❌ {name}: Error {response.status_code}")
    except Exception as e:
        results.append(f"❌ {name}: Exception - {str(e)}")
        print(f"❌ {name}: {str(e)}")

# Log trade
log_entry = {
    "timestamp": datetime.now().isoformat(),
    "pair": "XAUUSD",
    "direction": "BUY",
    "entry_range": [ENTRY_LOW, ENTRY_HIGH],
    "sl": SL,
    "tps": TPS,
    "position_size": POSITION_SIZE,
    "risk_usd": RISK_USD,
    "orders": results
}

with open("/home/chad-yi/.openclaw/workspace/agents/quanta/trade_log_20260213.json", "w") as f:
    json.dump(log_entry, f, indent=2)

print(f"\n📊 Trade logged. Monitoring for fills...")
