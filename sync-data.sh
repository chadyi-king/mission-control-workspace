#!/bin/bash
# Sync data.json between DATA/ and mission-control-dashboard/
# Usage: ./sync-data.sh [--push]

set -e

DATA_FILE="DATA/data.json"
DASHBOARD_FILE="mission-control-dashboard/data.json"

echo "=== Data.json Sync Tool ==="

# Check if DATA file exists
if [ ! -f "$DATA_FILE" ]; then
    echo "❌ ERROR: $DATA_FILE not found"
    exit 1
fi

# Check if dashboard file is a symlink
if [ -L "$DASHBOARD_FILE" ]; then
    echo "⚠️  Found symlink: $DASHBOARD_FILE"
    echo "   Replacing with actual file..."
    rm "$DASHBOARD_FILE"
fi

# Copy data file
echo "📋 Copying $DATA_FILE → $DASHBOARD_FILE"
cp "$DATA_FILE" "$DASHBOARD_FILE"

# Update timestamp to now
echo "🕐 Updating timestamp..."
python3 -c "
import json
from datetime import datetime
with open('$DASHBOARD_FILE', 'r') as f:
    data = json.load(f)
data['lastUpdated'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
data['updatedBy'] = 'CHAD_YI'
with open('$DASHBOARD_FILE', 'w') as f:
    json.dump(data, f, indent=2)
"

# Git operations
echo "📝 Staging changes..."
git add "$DASHBOARD_FILE"

# Commit if there are changes
if git diff --cached --quiet; then
    echo "✅ No changes to commit"
else
    echo "💾 Committing..."
    git commit -m "Sync: Update data.json from DATA/ ($(date +%Y-%m-%d %H:%M))"
    
    # Push if --push flag provided
    if [ "$1" == "--push" ]; then
        echo "🚀 Pushing to origin..."
        git push
        echo "✅ Sync complete! Render will update in ~30s"
    else
        echo "✅ Sync complete! Run with --push to deploy"
    fi
fi

echo ""
echo "📊 Current stats:"
grep -A5 '"stats":' "$DASHBOARD_FILE" | head -6
