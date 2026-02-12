# QUANTA SIGNAL VALIDATION RULES
## Prevent Trading on Old/Expired Signals

**Date:** 2026-02-13 01:55

---

## RULE 1: Only Trade NEW Signals

**Valid Signal:**
- Detected in real-time (within 30 seconds of posting)
- No "CLOSED" / "CANCELLED" / "EXPIRED" in recent messages
- Price still near entry range

**Invalid Signal (DO NOT TRADE):**
- Old signal (posted >5 minutes ago)
- Followed by "position closed" message
- Price already moved beyond entry range
- Marked as expired/cancelled

---

## RULE 2: Context Awareness

**Read RECENT messages (last 10) for context:**

```
Message -5: "XAUUSD BUY 2680-2685..." (OLD SIGNAL)
Message -4: "Position running +50 pips"
Message -3: "Move SL to BE"
Message -2: "Position closed at TP2"
Message -1: "Nice trade!"
Message 0 (NEW): "XAUUSD BUY 2690-2695..." (NEW SIGNAL)
```

**Analysis:**
- First signal: Position closed → EXPIRED, do NOT trade
- Second signal: Fresh → VALID, can trade

---

## RULE 3: Expiration Detection

**Keywords that INVALIDATE a signal:**
- "closed"
- "position closed"
- "cancelled"
- "expired"
- "stopped out"
- "hit SL"
- "done"
- "finished"

**Check:** If signal mentioned in last 5 messages with these words → EXPIRED

---

## RULE 4: Time-Based Validation

**Signal Age Check:**
- < 1 minute old: VALID (trade immediately)
- 1-5 minutes old: CHECK CONTEXT (may still be valid)
- > 5 minutes old: INVALID (likely expired)

---

## RULE 5: Price Check

**Before executing:**
- Current price should be NEAR entry range (±5 pips)
- If price moved >10 pips from entry → Signal stale
- If price hit SL already → Signal expired

---

## IMPLEMENTATION LOGIC

```python
async def validate_signal(self, signal, message_timestamp):
    """
    Validate if signal is fresh and tradeable
    """
    # 1. Check age
    age_seconds = (datetime.now() - message_timestamp).total_seconds()
    if age_seconds > 300:  # > 5 minutes
        return False, "Signal too old (>5 min)"
    
    # 2. Check recent context (last 10 messages)
    recent_messages = await self.get_recent_messages(10)
    
    for msg in recent_messages:
        msg_text = msg.text.lower()
        
        # Check if this signal mentioned as closed
        if signal['symbol'].lower() in msg_text:
            if any(word in msg_text for word in ['closed', 'cancelled', 'expired', 'stopped', 'hit sl', 'done']):
                return False, "Signal marked as closed/expired"
    
    # 3. Check current price
    current_price = await self.get_current_price(signal['symbol'])
    entry_mid = signal['entry_range']['mid']
    
    if abs(current_price - entry_mid) > 5:  # > 5 pips away
        return False, f"Price moved too far from entry (current: {current_price}, entry: {entry_mid})"
    
    # 4. All checks passed
    return True, "Signal valid"
```

---

## EXAMPLE SCENARIOS

### Scenario 1: Fresh Signal (TRADE)
```
10:00:00 - "XAUUSD BUY 2680-2685, SL 2675"
10:00:15 - [Quanta detects]
10:00:15 - [Validates: fresh, no context, price good]
10:00:20 - [EXECUTES TRADE]
```

### Scenario 2: Old Signal (NO TRADE)
```
09:30:00 - "XAUUSD BUY 2680-2685..." (30 min ago)
09:45:00 - "Position closed +100 pips"
10:00:00 - [Quanta starts, reads history]
10:00:01 - [Sees old signal + "closed" message]
10:00:01 - [SKIPS - signal expired]
```

### Scenario 3: Stale Price (NO TRADE)
```
10:00:00 - "XAUUSD BUY 2680-2685..."
10:02:00 - [Quanta detects] (2 min delay)
10:02:00 - [Current price: 2695] (moved 10+ pips)
10:02:00 - [SKIPS - price too far from entry]
```

---

## LOGGING

**When signal skipped:**
```json
{
  "timestamp": "2026-02-13T10:02:00",
  "event": "SIGNAL_SKIPPED",
  "reason": "Signal expired - position closed",
  "signal": {...},
  "context": "Position closed +100 pips at 09:45"
}
```

---

## SUMMARY

**Quanta will:**
1. ✅ Only trade FRESH signals (< 5 min old)
2. ✅ Read context to detect "closed/cancelled"
3. ✅ Verify price still near entry
4. ✅ Skip old/expired signals
5. ✅ Log why signal was skipped

**Never trade:**
- ❌ Old signals (> 5 min)
- ❌ Closed positions
- ❌ Expired signals
- ❌ Stale prices

---

*This prevents trading on outdated signals.*
