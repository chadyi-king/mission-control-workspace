# Skill: kimi-claw-helios
# Description: Mission Control Engineer with browser automation
# For: Kimi Claw on kimi.com

## Overview
Replaces Helios with browser-based monitoring capabilities.

## Capabilities
- Screenshot dashboard every 15 min
- Monitor Telegram Web (CallistoFX)
- Detect trading signals automatically
- Alert CHAD_YI immediately
- Execute simple browser tasks

## Tools Used
- screenshot
- browser (for Telegram Web)
- file_read (data.json)
- system_exec (ps, logs)
- telegram_send (alerts)
- cron (scheduling)

## Workflows

### 1. Dashboard Audit (Every 15 min)
```
1. Screenshot dashboard URL
2. Extract data from screenshot or read data.json
3. Verify lastUpdated timestamp
4. Count actual tasks vs reported
5. Send status to CHAD_YI
```

### 2. Telegram Monitor (Every 2 min)
```
1. Open web.telegram.org
2. Navigate to CallistoFX channel
3. Check for new messages
4. If signal detected:
   - Screenshot the message
   - Parse symbol/direction/SL/TP
   - Send alert to CHAD_YI immediately
5. Close browser (save resources)
```

### 3. Agent Health Check
```
1. Run: ps aux | grep agent_name
2. Check log file timestamps
3. If agent down:
   - Alert CHAD_YI
   - Suggest restart
```

## Communication with CHAD_YI

### Send Alert to CHAD_YI:
```yaml
target: telegram
recipient: 512366713
message_format: |
  🤖 Kimi-Claw-Helios Alert
  
  [Alert Type]: [Details]
  [Screenshot]: [attached if relevant]
  [Data]: [JSON/structured data]
  
  [Awaiting decision...]
```

### Receive Command from CHAD_YI:
```yaml
commands:
  - "execute_trade": Execute OANDA trade
  - "screenshot_now": Immediate screenshot
  - "check_agent": Verify specific agent
  - "update_status": Force status refresh
```

## Memory Files
- HEARTBEAT.md: Audit checklist
- DASHBOARD.md: Dashboard URL + access
- TELEGRAM_CONFIG.md: CallistoFX channel info
- AGENTS.md: Agent roster

## Cron Schedule
```
*/15 * * * *: dashboard_audit
*/2 * * * *: telegram_monitor
0 */6 * * *: full_system_report
```