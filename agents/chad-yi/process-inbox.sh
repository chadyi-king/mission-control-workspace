#!/bin/bash
# Process CHAD_YI inbox - Read and summarize agent messages

INBOX="/home/chad-yi/.openclaw/workspace/agents/chad-yi/inbox"
MEMORY="/home/chad-yi/.openclaw/workspace/agents/chad-yi/memory"
LOG="/home/chad-yi/.openclaw/workspace/agents/chad-yi/inbox-processor.log"

mkdir -p "$MEMORY/processed"

echo "[$(date '+%H:%M')] Processing inbox..." >> "$LOG"

# Count files
FILE_COUNT=$(ls -1 "$INBOX"/*.md 2>/dev/null | wc -l)
echo "Found $FILE_COUNT files" >> "$LOG"

if [ "$FILE_COUNT" -eq 0 ]; then
    echo "No files to process" >> "$LOG"
    exit 0
fi

# Process each file
for file in "$INBOX"/*.md; do
    [ -f "$file" ] || continue
    
    filename=$(basename "$file")
    echo "Processing: $filename" >> "$LOG"
    
    # Move to processed
    mv "$file" "$MEMORY/processed/"
    echo "  → Moved to processed/" >> "$LOG"
done

echo "[$(date '+%H:%M')] Done processing $FILE_COUNT files" >> "$LOG"
