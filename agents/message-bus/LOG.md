# Message Bus Log

## How It Works

### Sending a Message
1. Create a file in `message-bus/pending/`
2. Use format: `MSG-YYYYMMDD-NNN-SENDER-to-RECIPIENT.json`
3. CHAD_YI detects and routes it

### Receiving a Message
1. Check your `inbox/` folder
2. Read the message
3. Process the request
4. Write response to sender's inbox

### Example Workflow

**Escritor needs trading data:**
```
escritor/outbox/MSG-001.json → 
message-bus/pending/ → 
quanta/inbox/MSG-001.json → 
quanta processes → 
escritor/inbox/RESPONSE-001.json
```

## Current Pending Messages
| ID | From | To | Subject | Priority | Status |
|----|------|-----|---------|----------|--------|
| POK-1255 | Helios | Escritor | Status Poke (idle 2hrs) | NORMAL | Pending |
| POK-1255 | Helios | Quanta | Status Poke (idle 2hrs) | NORMAL | Pending |
| POK-1255 | Helios | MensaMusa | Status Poke (idle 2hrs) | NORMAL | Pending |
| POK-1255 | Helios | Autour | Status Poke (idle 2hrs) | NORMAL | Pending |
| POK-1055 | Helios | Escritor | Status Poke (idle 8.5hrs) | NORMAL | Pending |
| POK-1055 | Helios | Quanta | Status Poke (idle 8.5hrs) | NORMAL | Pending |
| POK-1055 | Helios | MensaMusa | Status Poke (idle 8.5hrs) | NORMAL | Pending |
| POK-1055 | Helios | Autour | Status Poke (idle 8.5hrs) | NORMAL | Pending |

## Recent Messages
| ID | From | To | Subject | Date |
|----|------|-----|---------|------|
| POK-1255 | Helios | All Agents | 15-min Agent Poke Cycle | 2026-02-14 12:55 |
| POK-1055 | Helios | All Agents | 15-min Agent Poke Cycle | 2026-02-14 10:55 |
| POK-1010 | Helios | All Agents | 15-min Agent Poke Cycle | 2026-02-14 10:10 |
| POK-2155 | Helios | Escritor/MensaMusa/Autour | Agent Poke Cycle | 2026-02-13 21:55 |
| POK-1940 | Helios | Escritor | 15-min Status Poke | 2026-02-13 |
| POK-1940 | Helios | Quanta | 15-min Status Poke | 2026-02-13 |
| POK-1940 | Helios | MensaMusa | 15-min Status Poke | 2026-02-13 |
| POK-1940 | Helios | Autour | 15-min Status Poke | 2026-02-13 |
| RPT-0830 | CHAD_YI | Archive | Coordination Report 08:30 | 2026-02-11 |
| RPT-0730 | CHAD_YI | Archive | Coordination Report 07:30 | 2026-02-11 |
| RPT-0630 | CHAD_YI | Archive | Coordination Report 06:30 | 2026-02-11 |
| RPT-0530 | CHAD_YI | Archive | Coordination Report 05:30 | 2026-02-11 |
| RPT-0430 | CHAD_YI | Archive | Coordination Report 04:30 | 2026-02-11 |

## Routing Rules
- Escritor ↔ Quanta: ALLOWED (research requests)
- Autour ↔ Kotler: ALLOWED (content strategy)
- All → Helios: ALLOWED (system issues)
- Any → CHAD_YI: ALWAYS ALLOWED (reports)