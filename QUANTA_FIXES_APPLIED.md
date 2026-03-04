# QUANTA V3 FIXES APPLIED — 2026-03-04

## Fixes Implemented

### ✅ FIX #1: Partial Close with Retry Logic
**File:** `position_manager.py`  
**Function:** `_close_partial()`

**Changes:**
- Changed return type from `None` to `bool`
- Added minimum unit validation (0.1 minimum)
- Added retry loop (3 attempts with exponential backoff: 1s, 2s)
- Added detailed logging for each attempt
- Added critical alert on failure (Telegram + Chad inbox)

**Result:** Partial closes now retry on failure instead of silently failing

---

### ✅ FIX #2: Tier Order Cancellation on TP1 Hit
**File:** `position_manager.py`  
**Location:** After TP1 hit, before SL move notification

**New Logic:**
```python
When TP1 hits:
  1. Close 10% of position ✅ (existing)
  2. Move SL to breakeven ✅ (existing)
  3. CANCEL remaining tier orders 🆕 (NEW)
  4. Send notification
```

**Why:** When TP1 hits and SL moves to breakeven, the trade is risk-free. 
The remaining tier limit orders (tier 2 and 3 at different entry prices) 
are no longer valid and should be cancelled to prevent unwanted additional entries.

**Implementation:**
- Gets message_id from trade state
- Finds pending orders with matching tag prefix (`qv3-{message_id}`)
- Cancels each pending order via OANDA API
- Logs cancellation count
- Sends notification with count of cancelled orders

---

### ✅ FIX #3: OANDA cancel_order Method
**File:** `oanda_client.py`  
**Function:** `cancel_order(order_id)`

**Implementation:**
- Supports dry_run mode (returns simulated response)
- PUT request to `/orders/{order_id}/cancel`
- Proper error handling

**Why:** Required for FIX #2 to work

---

### ✅ FIX #4: alert_critical in chad_inbox
**File:** `chad_inbox.py`  
**Function:** `alert_critical(message)`

**Implementation:**
- Writes critical alert to Chad's inbox
- Formatted with 🚨 emoji and "CRITICAL" header
- Includes full error message
- Prompts to check OANDA dashboard

**Why:** Required for FIX #1 to alert on partial close failures

---

## Summary of Changes

| File | Lines Changed | Key Change |
|------|---------------|------------|
| `position_manager.py` | ~50 lines | Retry logic + tier cancellation |
| `oanda_client.py` | ~10 lines | New cancel_order method |
| `chad_inbox.py` | ~10 lines | New alert_critical method |

**Total:** ~70 lines of code added/modified

---

## What This Fixes

### Before (Broken):
1. Partial close hits API error → Silently fails → $0 profit
2. TP1 hits, SL moves to BE → Tier 2/3 orders remain active → Unwanted entries
3. No immediate alerts on failures → You don't know what happened

### After (Fixed):
1. Partial close fails → Retries 3 times → If still fails, sends CRITICAL alert
2. TP1 hits → SL moves to BE → Tier 2/3 orders cancelled immediately → Clean trade
3. All failures send immediate alerts to Telegram + Chad inbox

---

## Testing Checklist Before Going Live

- [ ] Enable DRY_RUN=1 in .env
- [ ] Start Quanta
- [ ] Wait for signal
- [ ] Verify trade opens
- [ ] Manually check that TP1-TP5 logic works in dry run
- [ ] Verify tier cancellation message appears in logs
- [ ] Disable DRY_RUN (set to 0)
- [ ] Go live with small size

---

## Next Steps

1. **Paper test for 1 week** (optional but recommended)
2. **Go live with $10-20 risk per trade**
3. **Monitor first 5 trades closely**
4. **Scale up if working correctly**

---

*Fixes applied: 2026-03-04 00:15 SGT*  
*Status: READY FOR TESTING*
