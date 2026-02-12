# Agent Organization Structure

## Active Agents (Spawned)
| Agent | Role | Project | Status |
|-------|------|---------|--------|
| **CHAD_YI** | Orchestrator | All | ✅ Active |
| **Helios** | COO / Auditor | All | ✅ Active |
| **Quanta** | Trading Dev (Forex/Gold) | A5 | ✅ Active |
| **Escritor** | Storywriting Agent | A2 | ✅ Active |

## Defined But Not Spawned
| Agent | Role | Function | Dependencies |
|-------|------|----------|--------------|
| **Autour** | Scriptwriting Agent | YouTube, Streaming, Social Media content | Needs Clair's output |
| **Clair** | Streaming Scout | Finds winning content for Autour & Caleb | None (scout first) |
| **Kotler** | Marketing Ops | Content splicer/creator for all channels | Needs content from others |
| **Ledger** | Finance | Budget/accounting (Biz + Personal) | None |
| **Atlas** | High-Level Researcher | Finds info/skills for agent improvement | None |
| **E++** | Core Coding/Dev | Heavy engineering tasks | None |
| **MensaMusa** | Trading Agent (Options) | Options flow monitoring | Question: Overlap with Quanta? |
| **Abed** | Community Manager | Group chat moderation | Needs community first |

## Workflow Dependencies
```
Clair (Scout) → Finds content
       ↓
Autour (Scriptwriter) → Repurposes for YouTube/Social
       ↓
Kotler (Marketing) → Distributes to channels

Quanta (Forex) → Self-learning, audits ↓
                              MensaMusa (Options)

Helios (COO) → Audits ALL agents including CHAD_YI
```

## MensaMusa vs Quanta Clarification
| | Quanta | MensaMusa |
|---|---|---|
| **Market** | Forex + Gold (XAUUSD) | Stock Options |
| **Strategy** | Signal following | Unusual options flow |
| **Data** | CALLISTOFX Telegram | Moomoo/FlowAlgo |
| **Timeframe** | Intraday scalping | Swing/detecting big bets |
| **Quanta's role** | Self-trading + **Audits MensaMusa** | Execute when flow detected |

**Verdict:** Keep both. Quanta = forex specialist, MensaMusa = options specialist. Quanta audits MensaMusa's performance.

## Spawn Order (Suggested)
1. ✅ CHAD_YI (exists)
2. ✅ Helios (exists)
3. ✅ Quanta (exists)
4. ✅ Escritor (exists)
5. **Clair** → Content discovery (enables Autour)
6. **Autour** → KOE YouTube/TikTok scripts
7. **Ledger** → Track business finances
8. **Atlas** → Research for agent improvements
9. **Kotler** → Marketing distribution
10. **E++** → Heavy dev when needed
11. **MensaMusa** → Options (when ready)
12. **Abed** → When communities exist

## Notes
- Build one agent at a time for specific tasks
- Each agent needs: Skill.md, config, workspace, dashboard entry
- Helios audits ALL including CHAD_YI
- Quanta audits MensaMusa when spawned
