# Quanta Trading Configuration
# Set your risk parameters here

# Risk Management
MAX_RISK_PER_TRADE = 20  # $20 max risk per trade (as you specified)
ACCOUNT_BALANCE = 1000   # Your OANDA account balance
RISK_PERCENTAGE = 2      # 2% max risk per trade

# Position Sizing
DEFAULT_LOT_SIZE = 0.01  # Micro lots for testing
MAX_LOT_SIZE = 0.05      # Max position size

# Execution Strategy
SPLIT_POSITIONS = True           # Split into multiple positions for multiple TPs
PARTIAL_CLOSE_AT_TP1 = True      # Close 1/3 at TP1, move SL to breakeven
TRAILING_STOP_AFTER_TP2 = True   # Trail stop after TP2 hit

# OANDA Settings
OANDA_ACCOUNT_ID = "YOUR_ACCOUNT_ID"
OANDA_ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"
OANDA_ENVIRONMENT = "practice"  # "practice" or "live"

# Safety
PAPER_TRADING_MODE = True  # Set to False when ready for live
MAX_TRADES_PER_DAY = 5
MAX_DAILY_LOSS = 60  # Stop trading after $60 loss
