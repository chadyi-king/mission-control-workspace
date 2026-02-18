# QUANTA-V2 SETUP GUIDE
## Step-by-Step Instructions

---

## PHASE 1: OANDA Setup (5 minutes)

### Step 1: Get OANDA API Token
1. Go to https://www.oanda.com/demo-account
2. Create a demo account (or log in to existing)
3. Go to "Manage API Access"
4. Generate new token
5. **Copy the token** (looks like: `abc123def456...`)

### Step 2: Set Environment Variable
```bash
export OANDA_API_TOKEN=your_token_here
```

To make it permanent, add to `~/.bashrc` or `~/.zshrc`:
```bash
echo 'export OANDA_API_TOKEN=your_token_here' >> ~/.bashrc
source ~/.bashrc
```

---

## PHASE 2: Telegram Setup (10 minutes)

### Step 3: Get Telegram API Credentials
1. Go to https://my.telegram.org/apps
2. Log in with your phone number
3. Click "API development tools"
4. Create new application:
   - **App name**: QuantaTrader
   - **Short name**: quanta
   - **URL**: (leave blank)
   - **Platform**: Desktop
   - **Description**: Trading bot for CallistoFX
5. **Copy API_ID** (numbers like: `12345678`)
6. **Copy API_HASH** (long string like: `abc123def456...`)

### Step 4: Set Environment Variables
```bash
export TELEGRAM_API_ID=your_api_id
export TELEGRAM_API_HASH=your_api_hash
export TELEGRAM_PHONE=+6591234567  # Your phone with country code
```

Make permanent:
```bash
echo 'export TELEGRAM_API_ID=your_api_id' >> ~/.bashrc
echo 'export TELEGRAM_API_HASH=your_api_hash' >> ~/.bashrc
echo 'export TELEGRAM_PHONE=+6591234567' >> ~/.bashrc
source ~/.bashrc
```

---

## PHASE 3: Authentication (One-time, 2 minutes)

### Step 5: Run Telegram Authentication
```bash
cd /agents/quanta-v2
python3 telegram_monitor.py
```

**What happens:**
1. Script asks for your phone number (if not set)
2. Telegram sends you an SMS code
3. Enter the code
4. Script creates `quanta_session.session` file
5. Script finds "🚀 CallistoFx Premium Channel 🚀"
6. You see: "Telegram monitor started!"

**Press Ctrl+C to stop** (we'll start it properly later)

---

## PHASE 4: Test Everything (5 minutes)

### Step 6: Run Setup Script
```bash
cd /agents/quanta-v2
./setup.sh
```

This checks:
- ✅ Python installed
- ✅ Dependencies installed
- ✅ Environment variables set
- ✅ OANDA connection works
- ✅ Telegram authenticated
- ✅ Signal parsing works

### Step 7: Test Trade Execution (Paper Trading)
```bash
python3 main.py --test
```

**What happens:**
1. Quanta connects to OANDA
2. Parses test signal: "XAUUSD BUY 2680-2685, SL: 2675"
3. Calculates position size (should be ~2 units for $20 risk)
4. **Shows order preview** (does NOT execute yet)
5. You verify: "Is this correct?"

**Check the output:**
- Entry: 2682.5 (mid of range)
- SL: 2675
- Risk: ~$20 SGD
- Units: ~2 units

---

## PHASE 5: Deploy (10 minutes)

### Step 8: Deploy to Render

**Option A: GitHub + Render (Recommended)**
```bash
cd /root/.openclaw/workspace/mission-control-workspace
git add agents/quanta-v2/
git commit -m "Quanta v2 - stable trading bot"
git push
```

Then on Render:
1. Create new Web Service
2. Connect GitHub repo
3. Select `agents/quanta-v2`
4. Build command: `pip install -r requirements.txt`
5. Start command: `python main.py`
6. Add environment variables in Render dashboard

**Option B: Direct Render Deploy**
1. Go to https://dashboard.render.com
2. New → Web Service
3. Name: `quanta-v2`
4. Upload code as zip
5. Set environment variables
6. Deploy

---

## PHASE 6: Verify 24/7 Operation

### Step 9: Monitor Logs
```bash
# On Render dashboard, check logs
# Or if running locally:
tail -f quanta.log
```

**What to look for:**
- "Connected to Telegram!"
- "Heartbeat OK" (every 5 minutes)
- "New message" when signal arrives
- "Trade opened" with correct size
- "TP hit" when take profits
- "Runner activated" at +100 pips

### Step 10: Test with Real Signal (Paper Trading)

Wait for a signal in CallistoFX channel, or manually test:
```bash
python3 -c "
from main import QuantaV2
quanta = QuantaV2()
quanta.process_signal('XAUUSD BUY 2680-2685, SL: 2675, TP1: 2690, TP2: 2700')
"
```

**Verify:**
- Position size is small (~2 units)
- Risk is ~$20
- 3 orders placed (33%/33%/34%)
- SL set correctly

---

## TROUBLESHOOTING

### Problem: "OANDA connection failed"
**Solution:** Check API token, make sure it's demo account

### Problem: "Telegram authentication failed"
**Solution:** Delete `quanta_session.session` and run again

### Problem: "Channel not found"
**Solution:** Make sure you're subscribed to "🚀 CallistoFx Premium Channel 🚀"

### Problem: "Position size too large"
**Solution:** Check pip values in config.py, should be SGD not USD

### Problem: "Telegram disconnected"
**Solution:** Normal - auto-reconnect handles it. Check logs for "Reconnected"

---

## VERIFICATION CHECKLIST

Before going live, verify:

- [ ] OANDA demo account has $10,000+ balance
- [ ] API token works (tested with setup.sh)
- [ ] Telegram authenticated (session file exists)
- [ ] CallistoFX channel found
- [ ] Test trade shows correct position size (~2 units for XAUUSD)
- [ ] Risk verification shows ~$20
- [ ] 3-tier entry works
- [ ] TP/SL management works
- [ ] Runner activates at +100 pips
- [ ] Logs show "Heartbeat OK" every 5 minutes
- [ ] Auto-reconnect works (test by disconnecting WiFi briefly)

---

## GOING LIVE

When ready for real trading:

1. **Switch to OANDA live account:**
   - Get live API token from OANDA
   - Update `OANDA_ENVIRONMENT=live`
   - Start with small risk ($10 instead of $20)

2. **Monitor closely first week:**
   - Check logs daily
   - Verify all trades match signals
   - Ensure no unexpected large positions

3. **Gradual increase:**
   - Week 1: $10 risk per trade
   - Week 2: $15 risk per trade
   - Week 3+: $20 risk per trade

---

**Questions? Check logs first:**
```bash
tail -100 quanta.log
```
