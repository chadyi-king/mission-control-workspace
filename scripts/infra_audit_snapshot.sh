#!/usr/bin/env bash
set -euo pipefail

ISSUES=0
ok(){ echo "OK: $1"; }
issue(){ echo "ISSUE: $1"; ISSUES=$((ISSUES+1)); }
info(){ echo "INFO: $1"; }

ROOT="/home/chad-yi/.openclaw/workspace"
QUANTA="/home/chad-yi/mission-control-workspace/agents/quanta-v3"
DASH="$ROOT/mission-control-dashboard"
LIVE_DASH="https://red-sun-mission-control.onrender.com"

check_active(){
  local svc="$1"
  if systemctl --user is-active --quiet "$svc.service"; then ok "$svc active"; else issue "$svc inactive"; fi
}
check_inactive(){
  local svc="$1"
  if systemctl --user is-active --quiet "$svc.service"; then issue "$svc should be off but is active"; else ok "$svc off"; fi
}

check_active openclaw-gateway
check_active helios
check_active cerebronn
check_active forger
check_inactive mc-websocket
check_inactive gws-agent
check_inactive quanta
check_inactive chad-report-delivery

# Quanta v3 runtime (prefer systemd-owned PID, fall back to legacy manual PID)
QPID="$(systemctl --user show quanta-v3.service -p MainPID --value 2>/dev/null || true)"
if [ -n "$QPID" ] && [ "$QPID" != "0" ] && kill -0 "$QPID" 2>/dev/null; then
  ok "quanta-v3 process running pid=$QPID (systemd)"
else
  QPID="$(pgrep -f '/home/chad-yi/.venv/bin/python3? main.py --role all|/home/chad-yi/.venv/bin/python main.py --role all|main.py --role all' || true)"
  if [ -n "$QPID" ]; then
    ok "quanta-v3 process running pid=$QPID (manual)"
  else
    issue "quanta-v3 process not running"
  fi
fi

HB="$QUANTA/heartbeat.json"
if [ -f "$HB" ]; then
  age=$(( $(date +%s) - $(stat -c %Y "$HB") ))
  [ "$age" -le 1200 ] && ok "quanta heartbeat fresh (${age}s)" || issue "quanta heartbeat stale (${age}s)"
  dry=$(python3 - <<'PY'
import json
p='/home/chad-yi/mission-control-workspace/agents/quanta-v3/heartbeat.json'
with open(p) as f: d=json.load(f)
print(str(d.get('dry_run')).lower())
PY
)
  info "quanta dry_run=$dry"
else
  issue "missing quanta heartbeat.json"
fi

OT="$QUANTA/open_trades.json"
if [ -f "$OT" ]; then
  trades=$(python3 - <<'PY'
import json
p='/home/chad-yi/mission-control-workspace/agents/quanta-v3/open_trades.json'
with open(p) as f: d=json.load(f)
print(len(d) if isinstance(d,list) else -1)
PY
)
  info "quanta open_trades=$trades"
else
  issue "missing quanta open_trades.json"
fi

# Dashboard repo hygiene
if [ -d "$DASH/.git" ]; then
  if [ -n "$(git -C "$DASH" status --porcelain 2>/dev/null)" ]; then
    issue "mission-control-dashboard repo dirty"
  else
    ok "mission-control-dashboard repo clean"
  fi
else
  issue "mission-control-dashboard repo missing"
fi

# Live dashboard reachability
code=$(curl -L -s -o /dev/null -w '%{http_code}' "$LIVE_DASH" || true)
if [ "$code" = "200" ]; then ok "live dashboard reachable"; else issue "live dashboard http=$code"; fi

# ACTIVE.md freshness
if [ -f "$ROOT/ACTIVE.md" ]; then
  age=$(( $(date +%s) - $(stat -c %Y "$ROOT/ACTIVE.md") ))
  [ "$age" -le 172800 ] && ok "ACTIVE.md touched within 48h" || issue "ACTIVE.md stale (${age}s)"
else
  issue "ACTIVE.md missing"
fi

# summary line for easy parsing
if [ "$ISSUES" -eq 0 ]; then
  echo "SUMMARY: HEALTHY"
else
  echo "SUMMARY: $ISSUES issue(s)"
fi
