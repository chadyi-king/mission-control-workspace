#!/usr/bin/env python3
"""
CHAD_YI Auto-Responder for Helios Communication
Simple file-based message exchange (no daemon needed)
"""
import os
import json
import glob
from datetime import datetime

HELIOS_OUTBOX = "/home/chad-yi/.openclaw/workspace/agents/helios/outbox"
MY_OUTBOX = "/home/chad-yi/.openclaw/workspace/agents/chad-yi/outbox"
MY_INBOX = "/home/chad-yi/.openclaw/workspace/agents/chad-yi/inbox"

def check_helios_messages():
    """Check for unread messages from Helios"""
    # Look for recent non-audit messages
    messages = []
    
    # Check for message files (not audits)
    msg_pattern = os.path.join(HELIOS_OUTBOX, "msg-*.json")
    fix_pattern = os.path.join(HELIOS_OUTBOX, "fix-*.json")
    
    for pattern in [msg_pattern, fix_pattern]:
        for filepath in glob.glob(pattern):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    data['_filepath'] = filepath
                    data['_received_at'] = datetime.now().isoformat()
                    messages.append(data)
            except Exception as e:
                print(f"Error reading {filepath}: {e}")
    
    # Sort by timestamp
    messages.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return messages

def send_reply_to_helios(message_data, reply_content):
    """Send a reply back to Helios"""
    os.makedirs(MY_OUTBOX, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"reply-{timestamp}.json"
    filepath = os.path.join(MY_OUTBOX, filename)
    
    reply = {
        "from": "chad-yi",
        "to": "helios",
        "timestamp": datetime.now().isoformat(),
        "in_reply_to": message_data.get('message_id', 'unknown'),
        "content": reply_content,
        "status": "ok"
    }
    
    with open(filepath, 'w') as f:
        json.dump(reply, f, indent=2)
    
    print(f"Reply sent: {filepath}")
    return filepath

def process_pending_messages():
    """Main entry point - check and process all pending messages"""
    messages = check_helios_messages()
    
    if not messages:
        return None
    
    # Process the most recent message
    latest = messages[0]
    msg_type = latest.get('type', 'unknown')
    content = latest.get('content', latest)
    
    print(f"Received message from Helios: {msg_type}")
    
    # Auto-acknowledge
    reply = {
        "status": "received",
        "message_type": msg_type,
        "processed_at": datetime.now().isoformat(),
        "pending_action": False
    }
    
    send_reply_to_helios(latest, reply)
    
    return latest

if __name__ == "__main__":
    result = process_pending_messages()
    if result:
        print(json.dumps(result, indent=2))
    else:
        print("No pending messages from Helios")
