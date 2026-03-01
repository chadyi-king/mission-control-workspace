#!/usr/bin/env bash
set -euo pipefail

OPENCLAW_ROOT="/home/chad-yi/.openclaw/workspace"
MC_WORKSPACE="/home/chad-yi/mission-control-workspace"
PYTHON_BIN="${PYTHON_BIN:-/home/chad-yi/.venv/bin/python}"
HELIOS_PORT="${HELIOS_PORT:-8000}"
HELIOS_API_BASE="${HELIOS_API_BASE:-http://localhost:${HELIOS_PORT}}"
REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
BRIDGE_AGENT_NAME="${BRIDGE_AGENT_NAME:-chad}"

LOG_DIR="${OPENCLAW_ROOT}/runtime-logs"
PID_DIR="${OPENCLAW_ROOT}/runtime-pids"
mkdir -p "${LOG_DIR}" "${PID_DIR}"

HELIOS_PID_FILE="${PID_DIR}/helios.pid"
BRIDGE_PID_FILE="${PID_DIR}/bridge.pid"

if [[ -f "${HELIOS_PID_FILE}" ]] && kill -0 "$(cat "${HELIOS_PID_FILE}")" 2>/dev/null; then
  echo "[start] Helios already running (pid $(cat "${HELIOS_PID_FILE}"))"
else
  echo "[start] Starting Helios on port ${HELIOS_PORT}"
  (
    cd "${MC_WORKSPACE}"
    nohup "${PYTHON_BIN}" -m uvicorn helios.service:app --host 0.0.0.0 --port "${HELIOS_PORT}" >"${LOG_DIR}/helios.log" 2>&1 &
    echo $! > "${HELIOS_PID_FILE}"
  )
fi

if [[ -f "${BRIDGE_PID_FILE}" ]] && kill -0 "$(cat "${BRIDGE_PID_FILE}")" 2>/dev/null; then
  echo "[start] Bridge already running (pid $(cat "${BRIDGE_PID_FILE}"))"
else
  echo "[start] Starting Chad→Helios bridge"
  (
    cd "${OPENCLAW_ROOT}"
    nohup env \
      HELIOS_API_BASE="${HELIOS_API_BASE}" \
      REDIS_URL="${REDIS_URL}" \
      BRIDGE_AGENT_NAME="${BRIDGE_AGENT_NAME}" \
      "${PYTHON_BIN}" "${OPENCLAW_ROOT}/chad_helios_event_bridge.py" >"${LOG_DIR}/bridge.log" 2>&1 &
    echo $! > "${BRIDGE_PID_FILE}"
  )
fi

sleep 1

echo "[start] Health check: ${HELIOS_API_BASE}/api/health"
if curl -fsS "${HELIOS_API_BASE}/api/health" >/dev/null; then
  echo "[ok] Helios API is healthy"
else
  echo "[warn] Helios health check failed. Tail logs:"
  tail -n 40 "${LOG_DIR}/helios.log" || true
  tail -n 40 "${LOG_DIR}/bridge.log" || true
  exit 1
fi

echo "[done] Runtime started"
echo "       Helios log: ${LOG_DIR}/helios.log"
echo "       Bridge log: ${LOG_DIR}/bridge.log"
