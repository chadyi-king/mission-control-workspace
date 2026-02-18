# 🚨 OPENROUTER USAGE AUDIT REPORT
**Generated:** Feb 18, 2026 18:08 SGT  
**Status:** CRITICAL - Credit Exhaustion

---

## 💳 CURRENT CREDIT STATUS
**Error:** `402 This request requires more credits, or fewer max_tokens. You requested up to 30000 tokens, but can only afford 1262.`

**Remaining:** 1,262 tokens  
**Status:** CRITICAL - Near depletion

---

## 📋 ALL AGENTS USING OPENROUTER MODELS

### Active Agents with OpenRouter Configs:

| Agent | Model | Status | Notes |
|-------|-------|--------|-------|
| **Escritor** | `kimi-coding/k2p5` | active | Writer - RE:UNITE novel |
| **Autour** | `kimi-coding/k2p5` | active | Content - KOE scripts |
| **Quanta** | `kimi-coding/k2p5` | blocked | Trading - needs OANDA |
| **Forger** | `kimi-coding/kimi-k2-thinking` | active | Builder |

### Agent Config Files with OpenRouter:

| File | Model |
|------|-------|
| `agents/abed.json` | `kimi-coding/kimi-k2-thinking` |
| `agents/atlas.json` | `kimi-coding/kimi-k2-thinking` |
| `agents/ledger.json` | `kimi-coding/kimi-k2-thinking` |
| `agents/autour.json` | `kimi-coding/kimi-k2-thinking` |
| `agents/clair.json` | `kimi-coding/kimi-k2-thinking` |
| `agents/kotler.json` | `kimi-coding/kimi-k2-thinking` |
| `agents/escritor/AGENT_STATE.json` | `kimi-coding/k2p5` |
| `agents/autour/AGENT_STATE.json` | `kimi-coding/k2p5` |
| `agents/quanta/AGENT_STATE.json` | `kimi-coding/k2p5` |
| `agents/forger/AGENT_STATE.json` | `kimi-coding/kimi-k2-thinking` |

### Agents NOT Using OpenRouter:
| Agent | Model | Notes |
|-------|-------|-------|
| CHAD_YI | Default (kimi-coding/k2p5) | Main session - uses default |
| e++ | `openai/gpt-5.1-codex` | Different provider |
| mensamusa | `openai/gpt-5.1-codex` | Different provider |
| quanta.json | `openai/gpt-5.1-codex` | Different provider |
| pulsar | `gpt-mini` | Different provider |
| escritor.json | `ollama/qwen2.5:14b` | Local Ollama |

---

## 🔥 CRON JOBS USING OPENROUTER

### ⚠️ ENABLED (Still Running):

| Job ID | Name | Model | Status | Risk |
|--------|------|-------|--------|------|
| `a544de60-...` | CHAD_YI Redis Bridge | `kimi-coding/k2p5` | ✅ ENABLED | **HIGH** - Running every 5 min |

### ❌ ALREADY DISABLED:

| Job ID | Name | Model | Status | Disabled |
|--------|------|-------|--------|----------|
| `d1985c9c-...` | Helios Daytime Reports | `kimi-coding/kimi-k2-thinking` | ❌ DISABLED | Just now |
| `7409f506-...` | Helios Overnight | `kimi-coding/kimi-k2-thinking` | ❌ DISABLED | Just now |
| `6ea774c6-...` | Morning Briefing | `kimi-coding/kimi-k2-thinking` | ❌ DISABLED | Just now |
| `ef58f207-...` | Agent Status Check Day | `kimi-coding/kimi-k2-thinking` | ❌ DISABLED | Earlier |
| `d5dabc64-...` | Agent Status Check Night | `kimi-coding/kimi-k2-thinking` | ❌ DISABLED | Earlier |
| `445402b2-...` | Internal Coordination | `kimi-coding/kimi-k2-thinking` | ❌ DISABLED | Earlier |
| `99b92198-...` | Helios Dashboard Audit | `kimi-coding/kimi-k2-thinking` | ❌ DISABLED | Earlier |
| `f59dcce8-...` | Helios-CHAD_YI Task Check | `kimi-coding/kimi-k2-thinking` | ❌ DISABLED | Earlier |

### ✅ SAFE (No OpenRouter):

| Job ID | Name | Model | Status |
|--------|------|-------|--------|
| `e45c04b1-...` | Reminder: Search competitions | Default | ✅ ENABLED |
| `1d76137d-...` | Dashboard Heartbeat | Default | ❌ DISABLED |
| `62bb96e1-...` | Feature Verification | Default | ❌ DISABLED |
| Various others | System/default | Default | Mixed |

---

## 📊 HEARTBEAT.md CONFIGURATION

**Current:** Uses `kimi-coding/k2p5` via cron job `a544de60-...`

**Status:** Every 5 minutes  
**Risk:** HIGH - Frequent OpenRouter calls

---

## 🚨 IMMEDIATE ACTIONS REQUIRED

### 1. Disable Remaining OpenRouter Job NOW:
```bash
# Job to disable:
a544de60-1b5f-4feb-98a8-ac23bab0b82e
CHAD_YI Redis Bridge - Check Helios Messages
```

### 2. Top Up Credits OR Switch Models:
**Option A:** Add credits at https://openrouter.ai/settings/credits  
**Option B:** Switch all agents to default model (non-OpenRouter)

### 3. Agent Model Migration:
**Agents needing model change:**
- Escritor: `kimi-coding/k2p5` → default
- Autour: `kimi-coding/k2p5` → default
- Quanta: `kimi-coding/k2p5` → default
- Forger: `kimi-coding/kimi-k2-thinking` → default

---

## 💰 COST ANALYSIS

**Current Burn Rate:**
- Redis Bridge: Every 5 min = 288 calls/day
- Each call: Up to 30,000 tokens
- Estimated: ~8.6M tokens/day

**At 1,262 tokens remaining:**
- Time until exhaustion: **IMMEDIATE**
- Next cron run will fail

---

## ✅ RECOMMENDED FIX

**Immediate (Next 5 minutes):**
1. ✅ Disable `a544de60-...` cron job
2. 🔄 Switch to non-OpenRouter models
3. 💳 OR top up OpenRouter credits ($10-20)

**Short term (Today):**
1. Audit all agent configs
2. Remove OpenRouter model references
3. Test with default models

**Long term:**
1. Implement token budgeting
2. Set up credit alerts
3. Consider alternative providers

---

## 📁 FILES REQUIRING CHANGES

```
agents/escritor/AGENT_STATE.json     → Remove model field
agents/autour/AGENT_STATE.json       → Remove model field
agents/quanta/AGENT_STATE.json       → Remove model field
agents/forger/AGENT_STATE.json       → Remove model field
agents/abed.json                     → Remove model field
agents/atlas.json                    → Remove model field
agents/ledger.json                   → Remove model field
agents/autour.json                   → Remove model field
agents/clair.json                    → Remove model field
agents/kotler.json                   → Remove model field
```

---

## 🎯 NEXT STEPS

**Choose ONE:**

**Option 1: Keep OpenRouter (Paid)**
- Add credits: $10-20 minimum
- Re-enable jobs after credit add
- Monitor usage closely

**Option 2: Abandon OpenRouter (Free)**
- Disable `a544de60-...` job NOW
- Remove model fields from all agent configs
- Use default model only
- Re-test all agents

**Which option?**
