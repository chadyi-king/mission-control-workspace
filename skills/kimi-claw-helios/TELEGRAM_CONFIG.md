# Telegram Configuration - Kimi-Claw-Helios
# For monitoring CallistoFX trading signals

## Channel to Monitor
- **Name:** 🚀 CallistoFx Premium Channel 🚀
- **Type:** Private channel (subscription)
- **URL:** web.telegram.org/a/#-100[CHANNEL_ID]

## Login Method
- **Phone:** +6591593838
- **Auth:** SMS code or QR scan
- **Session:** Will persist in Kimi Claw cloud storage

## Signal Detection Pattern

### Format 1: Full Signal
```
🟢XAUUSD🟢
BUY RANGE: 4970-4975
SL 4965
TP : 4990/5000/5010/5020
```

### Format 2: Analysis Only
```
XAUUSD Analysis (16th Feb 2026)
🟢BUY ZONE: 4997.5 - 4945
```

### Format 3: Crypto
```
BTCUSD Analysis (16th Feb 2026)
🔴SELL ZONE: 68770 - 69230
```

## What to Capture

When signal detected:
1. **Full message text**
2. **Screenshot of message**
3. **Timestamp**
4. **Parse:** Symbol, Direction, Entry, SL, TP

## Alert to CHAD_YI

Send immediately to Telegram: 512366713

Format:
```
🚨 TRADING SIGNAL DETECTED

Channel: CallistoFX
Time: HH:MM:SS

Signal:
[Symbol] [Direction]
Entry: [Range]
SL: [Price]
TP: [Prices]

Screenshot: [attached]
Parsed Data: [JSON]

[CHAD_YI: Execute trade?]
```

## Automation Rules

1. **Do NOT auto-execute trades**
2. **Always wait for CHAD_YI approval**
3. **Screenshot for verification**
4. **Include parsed data for quick decision**

## Browser Automation Steps

```python
# Pseudocode for Kimi Claw
1. Open: https://web.telegram.org
2. Login with phone + SMS code (one-time)
3. Navigate to CallistoFX channel
4. Every 2 minutes:
   - Scroll to bottom
   - Check for new messages
   - If signal pattern found:
     - Screenshot
     - Parse text
     - Send alert to CHAD_YI
```

## Error Handling

- **If logged out:** Alert CHAD_YI, stop monitoring
- **If channel not found:** Alert CHAD_YI
- **If rate limited:** Back off, retry in 5 min
- **If screenshot fails:** Text-only alert

## Storage

Save screenshots to:
```
/signals/YYYY-MM-DD/
  - signal_HHMMSS.png
  - signal_HHMMSS.json
```

Keep 7 days of history.