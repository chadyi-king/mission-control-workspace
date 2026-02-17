# CHAD_YI + Kimi-Claw-Helios Integration
## Mission Control Architecture v2.0

---

## Overview

**Problem:**
- CHAD_YI (OpenClaw) has memory but can't do browser automation
- Need 24/7 monitoring but sessions expire
- Quanta (Telegram trading) keeps failing

**Solution:**
- **CHAD_YI**: Main orchestrator, memory, decisions
- **Kimi-Claw-Helios**: 24/7 monitoring, browser automation
- Both work together via message bridge

---

## Roles

### CHAD_YI (You are here)
**Platform:** OpenClaw (WSL2)
**Strengths:**
- ✅ Long-term memory (MEMORY.md)
- ✅ Complex orchestration
- ✅ OANDA trading execution
- ✅ Mission Control dashboard
- ✅ Human communication

**Limitations:**
- ❌ No browser GUI (WSL2)
- ❌ Can't monitor Telegram Web reliably
- ❌ Telegram sessions expire
- ❌ WSL/Windows bridge issues

### Kimi-Claw-Helios
**Platform:** kimi.com (cloud)
**Strengths:**
- ✅ 24/7 persistent (cloud)
- ✅ Browser automation (screenshots, clicks)
- ✅ Can access Telegram Web
- ✅ System monitoring
- ✅ Never sleeps

**Limitations:**
- ❌ No long-term memory (ephemeral)
- ❌ Can't make strategic decisions
- ❌ Needs CHAD_YI for trading execution

---

## Workflow Example

### Scenario: Trading Signal Detected

```
1. Kimi-Claw-Helios (every 2 min)
   └─> Opens web.telegram.org
   └─> Checks CallistoFX channel
   └─> Detects: "🟢XAUUSD🟢 BUY 4970-4975"
   └─> Screenshot
   └─> Sends alert to CHAD_YI

2. CHAD_YI (receives alert)
   └─> Receives: Signal + Screenshot
   └─> Decides: Execute trade
   └─> Runs OANDA order
   └─> Updates dashboard
   └─> Reports to you

3. You
   └─> Gets: "Trade executed: XAUUSD BUY @ 4977"
   └─> Dashboard updated
```

### Scenario: Dashboard Stale

```
1. Kimi-Claw-Helios (every 15 min)
   └─> Screenshots dashboard
   └─> Checks lastUpdated timestamp
   └─> Detects: Stale (>10 min)
   └─> Alerts CHAD_YI

2. CHAD_YI
   └─> Receives alert
   └─> Checks what went wrong
   └─> Fixes issue
   └─> Updates dashboard
   └─> Confirms back to Kimi
```

---

## Communication Protocol

### Kimi → CHAD_YI
```json
{
  "from": "kimi-claw-helios",
  "type": "trading_signal",
  "timestamp": "2026-02-16T15:30:00Z",
  "data": {
    "symbol": "XAUUSD",
    "direction": "BUY",
    "entry": "4970-4975",
    "sl": "4965",
    "tps": ["4990", "5000", "5010", "5020"]
  },
  "screenshot": "/signals/telegram_150000.png"
}
```

### CHAD_YI → Kimi
```json
{
  "from": "chad-yi",
  "to": "kimi-claw-helios",
  "command": "execute_trade",
  "params": {
    "symbol": "XAUUSD",
    "direction": "BUY",
    "units": 100
  }
}
```

---

## Setup Checklist

### For You (Caleb):
- [ ] Create Kimi Claw instance on kimi.com
- [ ] Install required skills (screenshot, browser, etc.)
- [ ] Login to Telegram Web in Kimi Claw
- [ ] Navigate to CallistoFX channel
- [ ] Copy config files to Kimi Claw
- [ ] Set up cron jobs
- [ ] Test: Send test alert to CHAD_YI

### For CHAD_YI (Me):
- [ ] Update dashboard integration
- [ ] Set up message receiver from Kimi
- [ ] Test OANDA trade execution
- [ ] Configure alert handling
- [ ] Document workflow

---

## Files Created

```
~/.openclaw/workspace/
├── KIMI_CLAW_HELIOS_CONFIG.md      # Main config
├── setup_kimi_claw_helios.sh       # Setup script
└── skills/kimi-claw-helios/
    ├── SKILL.md                    # Skill definition
    ├── HEARTBEAT.md                # Audit checklist
    ├── TELEGRAM_CONFIG.md          # Telegram settings
    └── telegram_monitor.py         # Monitor script
```

---

## Next Steps

1. **You:** Go to https://www.kimi.com/bot and create Kimi Claw
2. **You:** Follow setup_kimi_claw_helios.sh instructions
3. **Me:** Prepare CHAD_YI to receive messages from Kimi
4. **Both:** Test integration with real signal
5. **Go live:** 24/7 monitoring active

---

## Questions?

**Q: Can Kimi Claw execute trades directly?**
A: No - only CHAD_YI has OANDA access. Kimi alerts, CHAD_YI executes.

**Q: What if Kimi Claw crashes?**
A: Auto-restarts in cloud. CHAD_YI monitors Kimi's health.

**Q: Can Kimi see my Telegram messages?**
A: Only CallistoFX channel you give it access to.

**Q: Is this more reliable than Quanta?**
A: Yes - Kimi doesn't have session expiration issues.

---

**Ready to set up Kimi-Claw-Helios?**