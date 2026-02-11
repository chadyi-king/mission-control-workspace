#!/bin/bash
# Real-time Data Updater for Mission Control Dashboard
# This script updates data.json via GitHub API

REPO="chadyi-king/mission-control-dashboard"
FILE="data.json"
BRANCH="main"

# GitHub token should be set in environment
# export GITHUB_TOKEN="your_token_here"

if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN not set"
    exit 1
fi

# Get current file SHA
SHA=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
    "https://api.github.com/repos/$REPO/contents/$FILE?ref=$BRANCH" | \
    grep -o '"sha": "[^"]*"' | head -1 | cut -d'"' -f4)

if [ -z "$SHA" ]; then
    echo "Error: Could not get file SHA"
    exit 1
fi

# Read updated data.json
CONTENT=$(base64 -w 0 ~/.openclaw/workspace/mission-control-dashboard/data.json)

# Update file via API
curl -s -X PUT \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"message\": \"Auto-update data.json - $(date)\",
        \"content\": \"$CONTENT\",
        \"sha\": \"$SHA\",
        \"branch\": \"$BRANCH\"
    }" \
    "https://api.github.com/repos/$REPO/contents/$FILE"

echo "Data updated at $(date)"
