#!/bin/bash
#===============================================================================
# Robust Sync Script for Helios-Chad
# Self-healing, crash-proof sync with automatic recovery
#===============================================================================

set -o pipefail

#-------------------------------------------------------------------------------
# Configuration
#-------------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="/home/chad-yi/.openclaw/workspace"
LOG_DIR="$WORKSPACE_DIR/logs"
SYNC_DIR="$WORKSPACE_DIR/sync"
STATE_DIR="$SYNC_DIR"
LOCK_FILE="$STATE_DIR/sync.lock"
PID_FILE="$STATE_DIR/sync.pid"
MAX_RETRIES=5
RETRY_DELAY=10
GIT_REMOTE="origin"
GIT_BRANCH="main"
NODE_NAME="${NODE_NAME:-unknown}"

#-------------------------------------------------------------------------------
# Logging
#-------------------------------------------------------------------------------
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/sync.log"
ERROR_LOG="$LOG_DIR/sync_errors.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$ERROR_LOG" "$LOG_FILE"
}

#-------------------------------------------------------------------------------
# Alert Function
#-------------------------------------------------------------------------------
alert_caleb() {
    local message="$1"
    log "Sending alert: $message"
    
    # Try to send via openclaw message tool
    if command -v openclaw &> /dev/null; then
        openclaw message send --target "512366713" --message "🚨 SYNC ERROR: $message" 2>/dev/null || true
    fi
}

#-------------------------------------------------------------------------------
# Lock Management
#-------------------------------------------------------------------------------
acquire_lock() {
    if [[ -f "$LOCK_FILE" ]]; then
        local old_pid
        old_pid=$(cat "$LOCK_FILE" 2>/dev/null)
        if [[ -n "$old_pid" ]] && kill -0 "$old_pid" 2>/dev/null; then
            log "Sync already running (PID: $old_pid)"
            return 1
        else
            log "Removing stale lock file"
            rm -f "$LOCK_FILE"
        fi
    fi
    
    echo $$ > "$LOCK_FILE"
    echo $$ > "$PID_FILE"
    return 0
}

release_lock() {
    rm -f "$LOCK_FILE"
}

#-------------------------------------------------------------------------------
# Health Checks
#-------------------------------------------------------------------------------
check_git_repo() {
    if [[ ! -d "$WORKSPACE_DIR/.git" ]]; then
        log_error "Not a git repository: $WORKSPACE_DIR"
        return 1
    fi
    return 0
}

check_network() {
    # Check if we can reach the git remote
    if ! git -C "$WORKSPACE_DIR" ls-remote --exit-code "$GIT_REMOTE" &>/dev/null; then
        log_error "Cannot reach git remote: $GIT_REMOTE"
        return 1
    fi
    return 0
}

#-------------------------------------------------------------------------------
# Sync Operations
#-------------------------------------------------------------------------------
save_sync_state() {
    local status="$1"
    local message="${2:-}"
    
    cat > "$STATE_DIR/sync_state.json" << EOF
{
  "last_sync": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "status": "$status",
  "node": "$NODE_NAME",
  "message": "$message",
  "pid": $$
}
EOF
}

pull_changes() {
    log "Pulling changes from remote..."
    
    local attempt=1
    while [[ $attempt -le $MAX_RETRIES ]]; do
        if git -C "$WORKSPACE_DIR" pull --ff-only "$GIT_REMOTE" "$GIT_BRANCH" 2>&1 | tee -a "$LOG_FILE"; then
            log "Pull successful"
            return 0
        fi
        
        log "Pull failed (attempt $attempt/$MAX_RETRIES), retrying in ${RETRY_DELAY}s..."
        sleep $RETRY_DELAY
        ((attempt++))
    done
    
    log_error "Pull failed after $MAX_RETRIES attempts"
    return 1
}

push_changes() {
    log "Pushing changes to remote..."
    
    local attempt=1
    while [[ $attempt -le $MAX_RETRIES ]]; do
        if git -C "$WORKSPACE_DIR" push "$GIT_REMOTE" "$GIT_BRANCH" 2>&1 | tee -a "$LOG_FILE"; then
            log "Push successful"
            return 0
        fi
        
        log "Push failed (attempt $attempt/$MAX_RETRIES), retrying in ${RETRY_DELAY}s..."
        sleep $RETRY_DELAY
        ((attempt++))
    done
    
    log_error "Push failed after $MAX_RETRIES attempts"
    return 1
}

handle_conflicts() {
    log "Checking for conflicts..."
    
    if [[ -f "$SYNC_DIR/conflict_resolver.py" ]]; then
        python3 "$SYNC_DIR/conflict_resolver.py" --resolve 2>&1 | tee -a "$LOG_FILE"
        return $?
    else
        log_error "Conflict resolver not found"
        return 1
    fi
}

#-------------------------------------------------------------------------------
# Main Sync Function
#-------------------------------------------------------------------------------
run_sync() {
    log "=== Starting sync cycle ==="
    save_sync_state "in_progress"
    
    # Pre-flight checks
    if ! check_git_repo; then
        save_sync_state "failed" "Invalid git repository"
        return 1
    fi
    
    if ! check_network; then
        save_sync_state "failed" "Network unreachable"
        return 1
    fi
    
    # Stage any local changes
    log "Staging local changes..."
    git -C "$WORKSPACE_DIR" add -A 2>&1 | tee -a "$LOG_FILE" || true
    
    # Commit if there are changes
    if ! git -C "$WORKSPACE_DIR" diff --cached --quiet 2>/dev/null; then
        log "Committing local changes..."
        git -C "$WORKSPACE_DIR" commit -m "Auto-sync from $NODE_NAME at $(date -u +%Y-%m-%dT%H:%M:%SZ)" 2>&1 | tee -a "$LOG_FILE" || true
    fi
    
    # Always pull first (to avoid conflicts)
    if ! pull_changes; then
        # Check if it's a merge conflict
        if git -C "$WORKSPACE_DIR" diff --name-only --diff-filter=U | grep -q .; then
            log "Merge conflicts detected, attempting resolution..."
            if handle_conflicts; then
                log "Conflicts resolved"
            else
                save_sync_state "failed" "Unresolved conflicts"
                alert_caleb "Git conflicts could not be auto-resolved"
                return 1
            fi
        else
            save_sync_state "failed" "Pull failed"
            return 1
        fi
    fi
    
    # Push changes
    if ! push_changes; then
        save_sync_state "failed" "Push failed"
        alert_caleb "Failed to push changes after $MAX_RETRIES attempts"
        return 1
    fi
    
    save_sync_state "success"
    log "=== Sync cycle completed successfully ==="
    return 0
}

#-------------------------------------------------------------------------------
# Self-Healing Loop
#-------------------------------------------------------------------------------
main_loop() {
    log "Robust Sync started (PID: $$)"
    log "Node: $NODE_NAME"
    log "Workspace: $WORKSPACE_DIR"
    
    local consecutive_failures=0
    local max_consecutive_failures=3
    
    while true; do
        # Check if we should exit (for graceful shutdown)
        if [[ -f "$STATE_DIR/sync.stop" ]]; then
            log "Stop signal received, exiting..."
            rm -f "$STATE_DIR/sync.stop"
            break
        fi
        
        # Try to acquire lock
        if ! acquire_lock; then
            log "Another sync instance is running, waiting..."
            sleep 60
            continue
        fi
        
        # Run sync
        if run_sync; then
            consecutive_failures=0
        else
            ((consecutive_failures++))
            log_error "Sync failed (consecutive failures: $consecutive_failures)"
            
            if [[ $consecutive_failures -ge $max_consecutive_failures ]]; then
                alert_caleb "Sync has failed $consecutive_failures times in a row"
                consecutive_failures=0  # Reset after alerting
            fi
        fi
        
        release_lock
        
        # Wait before next sync
        log "Waiting 60 seconds before next sync..."
        sleep 60
    done
}

#-------------------------------------------------------------------------------
# Cleanup
#-------------------------------------------------------------------------------
cleanup() {
    log "Cleaning up..."
    release_lock
    rm -f "$PID_FILE"
    exit 0
}

trap cleanup SIGTERM SIGINT

#-------------------------------------------------------------------------------
# Memory Check
#-------------------------------------------------------------------------------
check_memory() {
    # Check if we're using too much memory
    local mem_usage
    mem_usage=$(ps -o rss= -p $$ 2>/dev/null || echo "0")
    mem_usage=$((mem_usage / 1024))  # Convert to MB
    
    if [[ $mem_usage -gt 500 ]]; then  # 500MB threshold
        log "Memory usage high (${mem_usage}MB), restarting..."
        return 1
    fi
    return 0
}

#-------------------------------------------------------------------------------
# Restart Logic
#-------------------------------------------------------------------------------
restart_with_delay() {
    local delay="${1:-10}"
    log "Restarting in ${delay}s..."
    sleep "$delay"
    exec "$0" "$@"
}

#-------------------------------------------------------------------------------
# Main Entry Point
#-------------------------------------------------------------------------------
main() {
    # Prevent duplicate instances
    if [[ -f "$PID_FILE" ]]; then
        local old_pid
        old_pid=$(cat "$PID_FILE" 2>/dev/null)
        if [[ -n "$old_pid" ]] && kill -0 "$old_pid" 2>/dev/null; then
            log "Sync already running (PID: $old_pid), exiting"
            exit 0
        fi
    fi
    
    # Create necessary directories
    mkdir -p "$LOG_DIR" "$SYNC_DIR" "$STATE_DIR"
    
    # Start main loop with crash protection
    while true; do
        main_loop
        exit_code=$?
        
        if [[ $exit_code -eq 0 ]]; then
            # Clean exit
            break
        else
            # Crash - restart with backoff
            log_error "Sync loop exited with code $exit_code, restarting..."
            restart_with_delay 30
        fi
    done
}

# Handle command line arguments
case "${1:-}" in
    --stop)
        log "Sending stop signal..."
        touch "$STATE_DIR/sync.stop"
        if [[ -f "$PID_FILE" ]]; then
            kill "$(cat "$PID_FILE")" 2>/dev/null || true
        fi
        exit 0
        ;;
    --status)
        if [[ -f "$STATE_DIR/sync_state.json" ]]; then
            cat "$STATE_DIR/sync_state.json"
        else
            echo '{"status": "unknown"}'
        fi
        exit 0
        ;;
    --once)
        # Run sync once and exit
        if acquire_lock; then
            run_sync
            exit_code=$?
            release_lock
            exit $exit_code
        else
            log "Sync already running"
            exit 1
        fi
        ;;
    *)
        main
        ;;
esac
