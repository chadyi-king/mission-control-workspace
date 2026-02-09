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
| - | - | - | - | - | - |

## Recent Messages
| ID | From | To | Subject | Date |
|----|------|-----|---------|------|
| - | - | - | - | - |

## Routing Rules
- Escritor ↔ Quanta: ALLOWED (research requests)
- Autour ↔ Kotler: ALLOWED (content strategy)
- All → Helios: ALLOWED (system issues)
- Any → CHAD_YI: ALWAYS ALLOWED (reports)