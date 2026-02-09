# OpenClaw Diagnostics Suite

Cost monitoring and system health diagnostics for OpenClaw agent operations.

## Scripts Overview

| Script | Purpose | Data Location |
|--------|---------|---------------|
| `token-tracker.py` | Track OpenAI API usage and costs | `data/token_usage.jsonl` |
| `rate-limit-monitor.py` | Monitor API rate limits | `data/rate_limit_config.json` |
| `agent-health.py` | Detect agent conflicts and crashes | `data/agent_state.json` |
| `cost-projector.py` | Predict remaining usage | `data/cost_projections.json` |

## Quick Start

### 1. Token Tracker

Track API calls and calculate costs:

```bash
# Log an API call manually
python token-tracker.py --log-api-call gpt-4o 1000 500

# Generate daily report
python token-tracker.py --report daily

# Generate weekly report
python token-tracker.py --report weekly

# Export to CSV
python token-tracker.py --export csv

# Show all reports
python token-tracker.py --report all
```

### 2. Rate Limit Monitor

Check API rate limit status:

```bash
# Check current status (default)
python rate-limit-monitor.py

# Check with alerts for limits
python rate-limit-monitor.py --check

# Set your OpenAI tier
python rate-limit-monitor.py --set-tier tier2

# Set custom limits
python rate-limit-monitor.py --set-limit 5000 450000 0

# Check actual OpenAI API headers
python rate-limit-monitor.py --headers
```

**Available Tiers:** free, tier1, tier2, tier3, tier4, tier5

### 3. Agent Health Monitor

Monitor agent processes and detect issues:

```bash
# Quick health check
python agent-health.py

# List active agents
python agent-health.py --list

# Watch mode (continuous monitoring)
python agent-health.py --watch

# Generate summary report
python agent-health.py --report --days 7
```

### 4. Cost Projector

Forecast usage and predict costs:

```bash
# Generate all forecasts
python cost-projector.py

# Check against specific budget
python cost-projector.py --budget 50.00 --period monthly

# Project end-of-month costs
python cost-projector.py --project-month

# JSON output for automation
python cost-projector.py --json
```

## Data Storage

All usage data is stored in `data/` directory:

| File | Content | Format |
|------|---------|--------|
| `token_usage.jsonl` | API call logs | JSON Lines |
| `rate_limit_config.json` | Rate limit settings | JSON |
| `rate_limit_alerts.log` | Rate limit alerts | Log |
| `agent_state.json` | Current agent state | JSON |
| `agent_crashes.log` | Crash history | JSON Lines |
| `agent_conflicts.log` | Conflict events | JSON Lines |
| `health_checks.log` | Health check history | JSON Lines |
| `cost_projections.json` | Latest projections | JSON |

## Environment Variables

```bash
# Change data directory
export DIAGNOSTICS_DATA_DIR=/path/to/data

# For API header checks
export OPENAI_API_KEY=sk-...

# Session tracking (set automatically by OpenClaw)
export OPENCLAW_SESSION_ID=session-123
export OPENCLAW_AGENT_ID=agent-456
```

## Integration Example

Add to your OpenClaw workflow:

```bash
# At start of session
python agent-health.py --check

# After API calls
python token-tracker.py --log-api-call gpt-4o 1500 800 --session-id $OPENCLAW_SESSION_ID

# Periodic checks
python rate-limit-monitor.py --check
python cost-projector.py --budget 100
```

## Automation

Run via cron for continuous monitoring:

```cron
# Check rate limits every 5 minutes
*/5 * * * * cd /path/to/diagnostics && python rate-limit-monitor.py --check

# Health check every minute
* * * * * cd /path/to/diagnostics && python agent-health.py --check

# Daily cost report at midnight
0 0 * * * cd /path/to/diagnostics && python cost-projector.py --project-month
```
