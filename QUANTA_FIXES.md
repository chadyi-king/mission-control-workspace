# QUANTA FIXES NEEDED

## Issues Found:

### 1. NOT RUNNING 24/7
- No systemd service installed
- Only runs when manually started
- Need: quanta.service

### 2. TOO MUCH LOGGING
- Logs EVERY message ("Message (not signal)")
- Fills up logs with noise
- Should only log ACTUAL signals

### 3. PAPER TRADING ONLY
- Code says: `execute_paper_trade()`
- No OANDA API integration
- Need: Live trading module

### 4. PARAMETER VERIFICATION NEEDED
- Need to verify: Entry mid, 10%/10%/20%/30%/30% exits
- SL to BE at TP1
- Trail after +100 pips

---

## FIXES REQUIRED:

### Fix 1: Reduce Logging
```python
# Change from:
print(f"💬 Message (not signal): {text[:50]}...")

# To:
# Only log signals, not every message
pass
```

### Fix 2: Create Service
- Create quanta.service
- Install with systemd
- Auto-restart on crash

### Fix 3: OANDA Integration
- Add oanda_executor.py
- API key from .env
- Live trade execution
- Position monitoring

### Fix 4: Verify Parameters
- Print exact calculations
- Show: Entry, Size, SL, TPs
- Confirm matches your rules

---

## IMPLEMENTATION ORDER:

**A) Quick Fixes (30 min):**
- Reduce logging
- Verify parameters
- Test signal detection

**B) Service Install (15 min):**
- Create quanta.service
- Install with sudo
- Start 24/7 monitoring

**C) OANDA Integration (2 hours):**
- Add live trading
- API integration
- Position monitoring
- Test with small trade

**Which do you want first?**
