#!/usr/bin/env bash
set -euo pipefail

OPENCLAW_ROOT="/home/chad-yi/.openclaw/workspace"
PID_DIR="${OPENCLAW_ROOT}/runtime-pids"
HELIOS_PORT="${HELIOS_PORT:-8000}"
HELIOS_API_BASE="${HELIOS_API_BASE:-http://localhost:${HELIOS_PORT}}"

show_proc() {
  local name="$1"
  local pid_file="${PID_DIR}/${name}.pid"
  if [[ -f "${pid_file}" ]]; then
    local pid
    pid="$(cat "${pid_file}")"
    if kill -0 "${pid}" 2>/dev/null; then
      echo "[status] ${name}: RUNNING (pid ${pid})"
    else
      echo "[status] ${name}: STALE PID (pid ${pid})"
    fi
  else
    echo "[status] ${name}: STOPPED"
  fi
}

show_proc helios
show_proc bridge

if curl -fsS "${HELIOS_API_BASE}/api/health" >/dev/null; then
  echo "[status] Helios API: HEALTHY (${HELIOS_API_BASE})"
else
  echo "[status] Helios API: UNREACHABLE (${HELIOS_API_BASE})"
fi
