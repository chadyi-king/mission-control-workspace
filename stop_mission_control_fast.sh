#!/usr/bin/env bash
set -euo pipefail

OPENCLAW_ROOT="/home/chad-yi/.openclaw/workspace"
PID_DIR="${OPENCLAW_ROOT}/runtime-pids"

stop_pid_file() {
  local name="$1"
  local pid_file="${PID_DIR}/${name}.pid"

  if [[ ! -f "${pid_file}" ]]; then
    echo "[stop] ${name}: no pid file"
    return
  fi

  local pid
  pid="$(cat "${pid_file}")"

  if kill -0 "${pid}" 2>/dev/null; then
    echo "[stop] ${name}: stopping pid ${pid}"
    kill "${pid}" || true
    sleep 1
    if kill -0 "${pid}" 2>/dev/null; then
      echo "[stop] ${name}: force kill pid ${pid}"
      kill -9 "${pid}" || true
    fi
  else
    echo "[stop] ${name}: process not running"
  fi

  rm -f "${pid_file}"
}

stop_pid_file bridge
stop_pid_file helios

echo "[done] Runtime stopped"
