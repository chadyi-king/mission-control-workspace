#!/bin/bash
# Quanta-v2 Setup Script
# Run this to set up everything

echo "=================================="
echo "QUANTA-V2 SETUP GUIDE"
echo "=================================="
echo ""

# Step 1: Check Python
echo "Step 1: Checking Python..."
python3 --version || { echo "Python 3 not found. Please install Python 3.11+"; exit 1; }

# Step 2: Install dependencies
echo ""
echo "Step 2: Installing dependencies..."
pip install -r requirements.txt

# Step 3: Check environment variables
echo ""
echo "Step 3: Checking environment variables..."

if [ -z "$OANDA_API_TOKEN" ]; then
    echo "❌ OANDA_API_TOKEN not set"
    echo "   Get it from: https://www.oanda.com/demo-account"
    echo "   Then run: export OANDA_API_TOKEN=your_token"
    MISSING=1
else
    echo "✅ OANDA_API_TOKEN is set"
fi

if [ -z "$TELEGRAM_API_ID" ]; then
    echo "❌ TELEGRAM_API_ID not set"
    echo "   Get it from: https://my.telegram.org/apps"
    echo "   Then run: export TELEGRAM_API_ID=your_api_id"
    MISSING=1
else
    echo "✅ TELEGRAM_API_ID is set"
fi

if [ -z "$TELEGRAM_API_HASH" ]; then
    echo "❌ TELEGRAM_API_HASH not set"
    echo "   Get it from: https://my.telegram.org/apps"
    echo "   Then run: export TELEGRAM_API_HASH=your_api_hash"
    MISSING=1
else
    echo "✅ TELEGRAM_API_HASH is set"
fi

if [ -z "$TELEGRAM_PHONE" ]; then
    echo "❌ TELEGRAM_PHONE not set"
    echo "   Format: +6591234567"
    echo "   Then run: export TELEGRAM_PHONE=your_phone"
    MISSING=1
else
    echo "✅ TELEGRAM_PHONE is set"
fi

if [ -n "$MISSING" ]; then
    echo ""
    echo "⚠️  Some environment variables are missing!"
    echo "   Set them and run this script again."
    exit 1
fi

echo ""
echo "✅ All environment variables are set!"

# Step 4: Test OANDA connection
echo ""
echo "Step 4: Testing OANDA connection..."
python3 -c "
from oanda_client import OandaClient
client = OandaClient()
account = client.get_account_info()
if account:
    print('✅ OANDA connection successful!')
    print(f'   Account: {account[\"account\"][\"id\"]}')
    print(f'   Balance: {account[\"account\"][\"balance\"]}')
else:
    print('❌ OANDA connection failed')
    exit(1)
"

# Step 5: Telegram authentication
echo ""
echo "Step 5: Telegram authentication..."
if [ -f "quanta_session.session" ]; then
    echo "✅ Session file exists (already authenticated)"
else
    echo "⚠️  Session file not found"
    echo "   Running authentication..."
    python3 telegram_monitor.py
    exit 0
fi

# Step 6: Test signal parsing
echo ""
echo "Step 6: Testing signal parsing..."
python3 -c "
from signal_parser import SignalParser
parser = SignalParser()

test_signals = [
    'XAUUSD BUY 2680-2685, SL: 2675, TP1: 2690',
    'EURUSD SELL 1.0850-1.0860, SL: 1.0875',
]

for signal in test_signals:
    result = parser.parse(signal)
    if result and parser.validate(result):
        print(f'✅ Parsed: {result[\"symbol\"]} {result[\"direction\"]}')
    else:
        print(f'❌ Failed to parse: {signal}')
"

# Step 7: Start Quanta
echo ""
echo "=================================="
echo "SETUP COMPLETE!"
echo "=================================="
echo ""
echo "To start Quanta in test mode:"
echo "   python3 main.py --test"
echo ""
echo "To start Quanta with Telegram:"
echo "   python3 main.py"
echo ""
echo "To deploy to Render:"
echo "   git add ."
echo "   git commit -m 'Quanta v2 ready'"
echo "   git push"
echo ""
