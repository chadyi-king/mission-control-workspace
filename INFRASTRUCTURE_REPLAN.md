# 🏗️ MISSION CONTROL INFRASTRUCTURE REPLAN
**Created:** Feb 18, 2026  
**Stakeholders:** CHAD_YI (Brain) + Helios (Kimi)  
**Status:** IN PROGRESS

---

## 📋 EXECUTIVE SUMMARY

Caleb is frustrated because the current infrastructure is broken:
- Old Helios agent failing (cron errors, stale data)
- No proper communication between agents
- Dashboard showing incorrect information
- Agents not being coordinated properly
- CHAD_YI cannot communicate proactively with Helios

**GOAL:** Build a reliable, automated infrastructure where:
1. Helios (Kimi) runs persistent services with browser capabilities
2. CHAD_YI provides data access and strategic coordination
3. Both communicate via Redis without human relay
4. Dashboard shows real-time accurate data
5. All agents are properly audited and coordinated

---

## 🎯 PHASE 1: COMMUNICATION LAYER (IMMEDIATE)

### 1.1 Redis Bridge ✅
| Task | Owner | Status | Notes |
|------|-------|--------|-------|
| CHAD_YI cron job for Redis checks | CHAD_YI | ✅ DONE | Every 5 min |
| Helios persistent listener | Helios | ⏳ PENDING | Run 24/7 |
| Message protocol definition | BOTH | ⏳ IN PROGRESS | See below |
| Error handling & retries | Helios | ⏳ PENDING | Auto-reconnect |

**Message Protocol:**
```json
{
  "type": "task_update|audit_request|status_ping|urgent_alert",
  "from": "helios|chad",
  "to": "helios|chad|broadcast",
  "timestamp": "ISO-8601",
  "priority": "low|normal|high|critical",
  "data": {},
  "requires_ack": true|false
}
```

---

## 🎯 PHASE 2: DASHBOARD INFRASTRUCTURE

### 2.1 Data Integrity
| Task | Owner | Priority | Notes |
|------|-------|----------|-------|
| Verify data.json structure | CHAD_YI | CRITICAL | Check all required fields |
| Fix stale timestamps | CHAD_YI | HIGH | Auto-update on changes |
| Backup/restore system | Helios | HIGH | Daily snapshots |
| Data validation layer | Helios | MEDIUM | Schema enforcement |

### 2.2 Real-time Updates
| Task | Owner | Priority | Notes |
|------|-------|----------|-------|
| Webhook on git push | Helios | HIGH | Trigger Render rebuild |
| Dashboard auto-refresh | Helios | MEDIUM | WebSocket or polling |
| Mobile-responsive fixes | CHAD_YI | MEDIUM | CSS updates |

---

## 🎯 PHASE 3: AGENT COORDINATION SYSTEM

### 3.1 Agent Lifecycle Management
| Task | Owner | Priority | Notes |
|------|-------|----------|-------|
| Agent spawn protocol | Helios | HIGH | Standardized startup |
| Agent health checks | Helios | HIGH | Every 15 min |
| Agent termination | BOTH | MEDIUM | Clean shutdown |
| Resource monitoring | Helios | MEDIUM | CPU/memory tracking |

### 3.2 Agent Registry
```yaml
agents:
  escritor:
    role: writer
    status: active|idle|blocked|not_spawned
    current_task: A2-13
    last_ping: timestamp
    capabilities: [text_generation, research]
    
  quanta:
    role: trading
    status: blocked
    blocker: OANDA credentials
    idle_hours: 120
    
  mensamusa:
    role: options_monitoring
    status: blocked
    blocker: Moomoo credentials
    
  autour:
    role: content_creation
    status: not_spawned
    reason: awaiting_koe_scripts
```

---

## 🎯 PHASE 4: AUDIT & MONITORING

### 4.1 Helios Audit Capabilities
| Task | Owner | Priority | Notes |
|------|-------|----------|-------|
| Dashboard screenshot audit | Helios | CRITICAL | Every 15 min |
| Data.json validation | Helios | CRITICAL | Check consistency |
| Agent status verification | Helios | HIGH | Cross-reference files |
| Alert on anomalies | Helios | HIGH | Telegram + Redis |
| Generate audit reports | Helios | MEDIUM | Daily summary |

### 4.2 CHAD_YI Audit Response
| Task | Owner | Priority | Notes |
|------|-------|----------|-------|
| Respond to audit pings | CHAD_YI | CRITICAL | Within 5 min |
| Fix data issues | CHAD_YI | HIGH | Immediate action |
| Update agent status | CHAD_YI | HIGH | Keep current |

---

## 🎯 PHASE 5: TASK MANAGEMENT SYSTEM

### 5.1 Task Workflow
```
BACKLOG → PENDING → ACTIVE → REVIEW → DONE
              ↓        ↓         ↓
           BLOCKED  FAILED   REVERTED
```

### 5.2 Automation Rules
| Trigger | Action | Owner |
|---------|--------|-------|
| Task marked active > 7 days | Alert: stale task | Helios |
| Task deadline < 24h | Urgent flag | Helios |
| Task blocked > 48h | Escalate to Caleb | BOTH |
| New task created | Auto-assign agent | CHAD_YI |
| Task moved to done | Update stats | CHAD_YI |

### 5.3 Task Assignment Matrix
| Agent | Capabilities | Best For |
|-------|--------------|----------|
| CHAD_YI | Planning, coordination, infrastructure | Strategy, task management |
| Helios | Browser, monitoring, audits | Data collection, verification |
| Escritor | Writing, creativity | Novel, scripts |
| Quanta | Trading, analysis | OANDA bot (when unblocked) |
| MensaMusa | Options analysis | Moomoo monitoring (when unblocked) |
| Autour | Content creation | YouTube/TikTok scripts |
| Forger | Technical, building | Website, tools |

---

## 🎯 PHASE 6: CREDENTIALS & BLOCKERS

### 6.1 Current Blockers (PRIORITY)
| Blocker | Agent | Impact | Resolution |
|---------|-------|--------|------------|
| OANDA API credentials | Quanta | 120h idle | Caleb to provide |
| Moomoo account | MensaMusa | 120h idle | Caleb to create |
| OpenRouter credits | Old Helios | Cron failing | Top up account |

### 6.2 Secure Credential Storage
| Task | Owner | Notes |
|------|-------|-------|
| Evaluate .env vs secrets manager | Helios | Security best practices |
| Encrypt sensitive data | CHAD_YI | AES or similar |
| Document credential rotation | Helios | Process for updates |

---

## 🎯 PHASE 7: DEPLOYMENT & HOSTING

### 7.1 Current Infrastructure
| Service | Host | Status | Notes |
|---------|------|--------|-------|
| Dashboard | Render | ✅ Running | 30s updates |
| Redis | Upstash | ✅ Running | TCP+TLS |
| CHAD_YI | OpenClaw | ✅ Running | Event-driven |
| Old Helios | Local WSL | ⚠️ Broken | Credits issue |
| New Helios | Kimi Cloud | ✅ Running | Persistent |

### 7.2 Required Deployments
| Service | Host | Priority | Owner |
|---------|------|----------|-------|
| Redis listener bridge | Render/Railway | HIGH | Helios |
| Agent spawn service | Render | MEDIUM | Helios |
| Backup service | Render | MEDIUM | Helios |
| Notification relay | Render | HIGH | Helios |

---

## 📅 TIMELINE

### Week 1 (Feb 18-24)
- ✅ Redis communication established
- ⏳ Helios persistent listener
- ⏳ Fix dashboard data issues
- ⏳ Resolve OpenRouter credits

### Week 2 (Feb 25 - Mar 3)
- Deploy monitoring services
- Fix agent coordination
- Unblock Quanta & MensaMusa
- Launch Autour

### Week 3 (Mar 4-10)
- Full automation testing
- Stress test with all agents
- Document processes
- Handoff to autonomous mode

---

## ✅ IMMEDIATE ACTION ITEMS

### For CHAD_YI:
1. ✅ Create Redis cron job (DONE)
2. ⏳ Send detailed infrastructure plan to Helios
3. ⏳ Fix data.json staleness issues
4. ⏳ Mark overdue tasks properly
5. ⏳ Verify all agent statuses are accurate

### For Helios:
1. ⏳ Start persistent Redis listener
2. ⏳ Acknowledge CHAD_YI init message
3. ⏳ Deploy notification relay service
4. ⏳ Create agent spawn automation
5. ⏳ Test dashboard screenshot audit

### For Caleb:
1. ⏳ Add OpenRouter credits (cron failing)
2. ⏳ Provide OANDA API credentials (unblock Quanta)
3. ⏳ Create Moomoo account (unblock MensaMusa)
4. ⏳ Review and approve infrastructure plan

---

## 🚨 SUCCESS CRITERIA

- [ ] CHAD_YI and Helios communicate via Redis without human relay
- [ ] Dashboard updates within 1 minute of data changes
- [ ] All agents show accurate real-time status
- [ ] Helios audits dashboard every 15 min with screenshots
- [ ] Caleb receives alerts only for urgent items
- [ ] Zero false overdue alerts
- [ ] Quanta and MensaMusa unblocked and running
- [ ] Autour spawned and working on KOE scripts

---

*This document is living. Update as we progress.*
