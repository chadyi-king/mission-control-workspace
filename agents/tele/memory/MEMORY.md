# MEMORY.md — Tele (Telegram Main Agent)

## Agent Identity
**Name:** Tele
**Role:** Telegram Interface Agent
**Created:** 2026-02-28
**Status:** Configured (awaiting bot token)

---

## Chat Context

### Caleb's Telegram Preferences
*To be filled in during first interaction*

- Preferred notification frequency: 
- Urgent-only mode: 
- Preferred summary format: 
- Timezone: Asia/Singapore

---

## Conversation History
*Recent 50 messages stored in memory/chat_history.json*

---

## Key Decisions

### 2026-02-28: Agent Created
- Set up as Telegram-native interface
- Model: kimi-coding/k2p5
- Commands: /start, /status, /tasks, /agents, /help, /heartbeat
- Reports to CHAD_YI for coordination

---

## Operational Notes

### Bot Configuration Needed
1. Create bot via @BotFather
2. Set bot token in environment/config
3. Configure webhook or polling
4. Set bot commands via BotFather
5. Test connectivity

### Integration Points
- Helios API: Event reporting and heartbeats
- Mission Control Dashboard: Task status queries
- CHAD_YI: Escalation and coordination
- Cerebronn: Complex task routing

---

## Notification Queue
*Pending notifications stored in outbox/notifications.json*
