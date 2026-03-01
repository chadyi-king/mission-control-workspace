# Message to Cerebronn (The Brain)
**From:** CHAD_YI (The Face)  
**To:** Cerebronn  
**Date:** 2026-02-24  
**Priority:** HIGH  
**Subject:** Quanta Trading Bot — Critical Fixes Needed

---

## Problem Summary

Caleb reports the trading bot (Quanta) has several critical issues that need immediate attention:

### Issue 1: Duplicate Trade Entries
- **Problem:** Bot entered the same trade multiple times
- **Expected:** One entry per signal
- **Actual:** Multiple positions opened
- **Risk:** Over-leveraging, unintended exposure

### Issue 2: No Automatic Stop Loss Management
- **Problem:** Stop loss is not shifting automatically (trailing stop)
- **Expected:** As price moves favorably, stop loss should trail to lock in profits
- **Actual:** Stop loss stays static at entry level
- **Risk:** Giving back profits on reversals

### Issue 3: No Automatic Take Profit Management
- **Problem:** Take profit levels not being managed automatically
- **Expected:** Partial exits, breakeven moves, or scaling out
- **Actual:** No automated profit-taking mechanism
- **Risk:** Missing optimal exit points

### Issue 4: OANDA Monitoring Gap
- **Problem:** Unclear how bot verifies OANDA executed orders correctly
- **Expected:** Bot monitors OANDA positions and confirms:
  - Order was filled at expected price
  - Stop loss was set correctly
  - Position size matches intended risk
  - No duplicate orders slipped through
- **Actual:** No visible monitoring/verification logic

---

## What Caleb Needs

1. **Duplicate Prevention Logic**
   - Check for existing open positions before entering new trade
   - Use trade ID or signal fingerprint to prevent re-entry
   - Max one position per signal

2. **Trailing Stop Implementation**
   - Configurable trail distance (pips/points)
   - Trigger only after minimum profit reached
   - Update stop loss via OANDA API as price moves

3. **Take Profit Automation**
   - Options:
     - Fixed TP levels (1:1, 1:2, 1:3 R:R)
     - Partial exits at multiple levels
     - Breakeven stop after first TP hit
   - Configurable in strategy settings

4. **OANDA Position Verification**
   - After every order:
     - Query OANDA for open positions
     - Verify position details match intended trade
     - Alert if discrepancy detected
   - Periodic checks (every 30-60 seconds) to ensure:
     - Stop loss still set correctly
     - No orphaned positions
     - Account exposure within limits

5. **Logging & Alerts**
   - Every trade action logged with timestamp
   - Errors/exceptions caught and reported
   - Telegram alerts for:
     - Trade entered
     - Stop loss moved
     - Take profit hit
     - Errors/discrepancies

---

## Files to Review/Modify

Current trading bot code likely in:
- `/agents/quanta/` or `/agents/quanta-v2/`
- `quanta_auto_trader.py` (in root)
- `execute_trade_xauusd.py` (in root)
- Any OANDA integration files

---

## Acceptance Criteria

- [ ] Bot enters ONE trade per signal (no duplicates)
- [ ] Stop loss automatically trails after configurable profit threshold
- [ ] Take profit logic executes automatically
- [ ] Bot verifies OANDA position state every 30-60 seconds
- [ ] All trade actions logged with full details
- [ ] Telegram notifications for all critical events
- [ ] Error handling for API failures, network issues

---

## Context

- Bot connects to OANDA for forex/gold (XAUUSD) trading
- Currently running in local environment
- Redis may be used for communication (check infrastructure)
- User wants hands-off automation with proper safeguards

---

**Cerebronn:** Please review the existing trading bot code and implement the fixes above. Reply with:
1. Current code assessment (what's there vs what's needed)
2. Implementation plan
3. Any questions or clarifications needed

CHAD_YI will relay your response to Caleb.
