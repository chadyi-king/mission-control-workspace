# OANDA API Configuration for Quanta Trading Agent

# API Credentials
OANDA_API_KEY = "8d4ff0fbea2b109c515a956784596208-be028efcd5faae816357345ff32c3bac"
OANDA_ACCOUNT_ID = "001-003-8520002-001"

# Environment: "practice" for demo, "live" for real money
OANDA_ENVIRONMENT = "live"  # LIVE account with SGD 2,004.57

# API Base URL
if OANDA_ENVIRONMENT == "live":
    BASE_URL = "https://api-fxtrade.oanda.com/v3"
else:
    BASE_URL = "https://api-fxpractice.oanda.com/v3"

# Trading Settings
RISK_PERCENT_PER_TRADE = 1.0  # Risk 1% per trade
MAX_OPEN_POSITIONS = 5
DEFAULT_STOP_LOSS_PIPS = 20

# CALLISTOFX Integration
CALLISTOFX_CHANNEL = "CALLISTOFX"
AUTO_EXECUTE_SIGNALS = False  # Set to True after testing
NOTIFY_ON_SIGNAL = True
