import os
from dotenv import load_dotenv

load_dotenv()

# OANDA Settings
OANDA_API_TOKEN = os.getenv('OANDA_API_TOKEN', '8d4ff0fbea2b109c515a956784596208-be028efcd5faae816357345ff32c3bac')
OANDA_ACCOUNT_ID = os.getenv('OANDA_ACCOUNT_ID', '001-003-8520002-001')
OANDA_ENVIRONMENT = os.getenv('OANDA_ENVIRONMENT', 'live')

# Risk Settings
RISK_AMOUNT = float(os.getenv('RISK_AMOUNT', 20.0))  # $20 fixed for first 20 trades
RISK_PERCENT_AFTER_20 = float(os.getenv('RISK_PERCENT', 0.01))  # 1% after 20 trades
TRADE_COUNT_FILE = 'trade_count.json'

# Trading Settings
MAX_SPREAD_PIPS = 3.0

# Pip Values in SGD (per 1 unit) - CRITICAL: Account currency is SGD
# Based on OANDA screenshots: 1 unit XAUUSD = 0.01 SGD per pip
DEFAULT_PIP_VALUES = {
    'XAUUSD': 0.01,      # 1 unit = 0.01 SGD per pip (verified from OANDA screenshot)
    'XAGUSD': 0.001,     # Silver typically 1/10 of gold
    'EURUSD': 0.0001,    # Forex pairs ~0.0001 SGD per unit per pip
    'GBPUSD': 0.0001,
    'USDJPY': 0.0001,
}

# Lot sizes for reference
LOT_SIZES = {
    'XAUUSD': 100,       # 1 lot = 100 units
    'XAGUSD': 100,       # 1 lot = 100 units
    'EURUSD': 100000,    # 1 lot = 100,000 units
    'GBPUSD': 100000,
    'USDJPY': 100000,
}

# 3-Tier Entry
TIER_SPLITS = [0.33, 0.33, 0.34]

# Take Profit Levels (pips)
TP_LEVELS = [20, 40, 60, 80, 100]
TP_CLOSE_PERCENT = 0.10  # Close 10% at each TP

# Runner Settings
RUNNER_ACTIVATION_PIPS = 100
RUNNER_TRAIL_DISTANCE = 100  # Trail SL 100 pips behind
RUNNER_CLOSE_PERCENT = 0.10  # Close 10% of remaining every 50 pips
RUNNER_STEP_PIPS = 50

# Stop Loss Management
SL_BE_ACTIVATION = 20  # Move to BE at +20 pips
SL_LOCK_ACTIVATION = 50  # Lock +20 pips at +50
SL_LOCK_PROFIT = 20

# Redis Settings
REDIS_URL = os.getenv('REDIS_URL', 'redis://default:AYylAAIncDI4Y2EwM2YyNWM4ZDk0N2M4OTJmMmE3ODFiYjEwYWYzYnAyMzYwMDU@national-gar-36005.upstash.io:6379')
CHANNEL_IN = 'callisto→quanta'
CHANNEL_OUT = 'quanta→helios'

# Learning
LEARNING_DB = 'learning_database.jsonl'
STRATEGY_KEYWORDS = [
    'breakout', 'support', 'resistance', 'trend', 'range',
    'scalping', 'swing', 'bounce', 'momentum', 'reversal'
]
