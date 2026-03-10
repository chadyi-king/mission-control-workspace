#!/bin/bash
# Daily Backup Script for CHAD_YI
# Run this every day to backup identity and memory
# Can be run manually or via cron

BACKUP_DIR="/home/chad-yi/.openclaw/workspace/backups/$(date +%Y-%m-%d)"
LOG_FILE="/home/chad-yi/.openclaw/workspace/backups/backup.log"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting daily backup..." >> "$LOG_FILE"

# Backup identity files (core who I am)
cp /home/chad-yi/.openclaw/agents/main/SOUL.md "$BACKUP_DIR/" 2>/dev/null
cp /home/chad-yi/.openclaw/agents/main/SKILL.md "$BACKUP_DIR/" 2>/dev/null
cp /home/chad-yi/.openclaw/agents/main/LEARNING.md "$BACKUP_DIR/" 2>/dev/null
cp /home/chad-yi/.openclaw/agents/main/current-task.md "$BACKUP_DIR/" 2>/dev/null

# Backup workspace copies (git-tracked)
cp /home/chad-yi/.openclaw/workspace/agents/chad-yi/SOUL.md "$BACKUP_DIR/SOUL-workspace.md" 2>/dev/null
cp /home/chad-yi/.openclaw/workspace/agents/chad-yi/LEARNING.md "$BACKUP_DIR/LEARNING-workspace.md" 2>/dev/null
cp /home/chad-yi/.openclaw/workspace/agents/chad-yi/REPORTING_PROTOCOL.md "$BACKUP_DIR/" 2>/dev/null

# Backup MEMORY.md (critical long-term memory)
cp /home/chad-yi/.openclaw/workspace/MEMORY.md "$BACKUP_DIR/" 2>/dev/null

# Backup ACTIVE.md (task source of truth)
cp /home/chad-yi/.openclaw/workspace/ACTIVE.md "$BACKUP_DIR/" 2>/dev/null

# Backup USER.md (who Caleb is)
cp /home/chad-yi/.openclaw/workspace/USER.md "$BACKUP_DIR/" 2>/dev/null

# Backup daily memory files
mkdir -p "$BACKUP_DIR/memory"
cp /home/chad-yi/.openclaw/workspace/memory/*.md "$BACKUP_DIR/memory/" 2>/dev/null

# Git commit everything
cd /home/chad-yi/.openclaw/workspace
git add -A
git commit -m "chore: Daily backup $(date +%Y-%m-%d) - auto backup of identity, memory, tasks" 2>/dev/null || true
git push upstream master 2>/dev/null || true

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Backup complete: $BACKUP_DIR" >> "$LOG_FILE"
echo "Backup saved to: $BACKUP_DIR"
