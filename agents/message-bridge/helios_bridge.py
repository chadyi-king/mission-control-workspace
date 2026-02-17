#!/usr/bin/env python3
"""
Helios Message Bridge - Pulls messages from GitHub and routes to local message bus
Run this every heartbeat to sync with remote Helios
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

# Paths
WORKSPACE = "/home/chad-yi/.openclaw/workspace"
MESSAGES_DIR = os.path.join(WORKSPACE, "messages")
LOCAL_BUS = os.path.join(WORKSPACE, "agents", "message-bus")
HELIOS_INBOX = os.path.join(LOCAL_BUS, "inbox", "helios")
CHAD_YI_INBOX = os.path.join(LOCAL_BUS, "inbox", "chad_yi")
ARCHIVE = os.path.join(MESSAGES_DIR, "archive")

def ensure_dirs():
    """Create necessary directories"""
    for d in [MESSAGES_DIR, HELIOS_INBOX, CHAD_YI_INBOX, ARCHIVE]:
        os.makedirs(d, exist_ok=True)

def sync_from_github():
    """
    Pull latest messages from GitHub.
    In production: git pull origin main
    For now: manual sync
    """
    print("[BRIDGE] Syncing from GitHub...")
    # TODO: Implement git pull
    return True

def route_helios_messages():
    """
    Route messages from Helios inbox to local message bus
    """
    helios_messages = os.path.join(MESSAGES_DIR, "helios", "outbox")
    
    if not os.path.exists(helios_messages):
        print("[BRIDGE] No Helios messages directory yet")
        return 0
    
    messages = sorted([f for f in os.listdir(helios_messages) if f.endswith('.json')])
    routed = 0
    
    for msg_file in messages:
        src = os.path.join(helios_messages, msg_file)
        
        try:
            with open(src, 'r') as f:
                msg = json.load(f)
            
            # Determine destination based on 'to' field
            to_agent = msg.get('to', 'chad-yi')
            
            if to_agent == 'chad-yi':
                dest = os.path.join(CHAD_YI_INBOX, msg_file)
            elif to_agent == 'broadcast':
                dest = os.path.join(LOCAL_BUS, "broadcast", msg_file)
            else:
                dest = os.path.join(LOCAL_BUS, f"{to_agent}-to-helios", msg_file)
            
            # Copy to destination
            shutil.copy2(src, dest)
            
            # Archive original
            archive_path = os.path.join(ARCHIVE, f"helios-{msg_file}")
            shutil.move(src, archive_path)
            
            print(f"[BRIDGE] Routed: {msg_file} -> {to_agent}")
            routed += 1
            
        except Exception as e:
            print(f"[BRIDGE] Error routing {msg_file}: {e}")
    
    return routed

def send_to_helios(subject, content, msg_type="response", priority="normal"):
    """
    Send a message to Helios (writes to outbox, ready for git push)
    """
    chad_yi_outbox = os.path.join(MESSAGES_DIR, "chad-yi", "outbox")
    os.makedirs(chad_yi_outbox, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    msg_id = f"msg-{timestamp}"
    
    message = {
        "id": msg_id,
        "from": "chad-yi",
        "to": "helios",
        "timestamp": datetime.now().isoformat(),
        "type": msg_type,
        "priority": priority,
        "subject": subject,
        "content": content,
        "requiresResponse": False
    }
    
    filepath = os.path.join(chad_yi_outbox, f"{msg_id}.json")
    with open(filepath, 'w') as f:
        json.dump(message, f, indent=2)
    
    print(f"[BRIDGE] Message queued for Helios: {msg_id}")
    return filepath

def check_for_urgent():
    """
    Check if any urgent messages need immediate attention
    """
    urgent = []
    
    # Check CHAD_YI inbox
    if os.path.exists(CHAD_YI_INBOX):
        for f in os.listdir(CHAD_YI_INBOX):
            if f.endswith('.json'):
                try:
                    with open(os.path.join(CHAD_YI_INBOX, f)) as fp:
                        msg = json.load(fp)
                    if msg.get('priority') in ['high', 'urgent']:
                        urgent.append(msg)
                except:
                    pass
    
    return urgent

def main():
    """Main bridge function"""
    print("=" * 50)
    print(f"[BRIDGE] Helios Message Bridge - {datetime.now()}")
    print("=" * 50)
    
    ensure_dirs()
    
    # Sync from GitHub
    sync_from_github()
    
    # Route messages
    routed = route_helios_messages()
    print(f"[BRIDGE] Routed {routed} messages from Helios")
    
    # Check for urgent items
    urgent = check_for_urgent()
    if urgent:
        print(f"[BRIDGE] ⚠️  {len(urgent)} URGENT messages waiting")
        for msg in urgent:
            print(f"  - {msg.get('subject')}")
    
    print("[BRIDGE] Sync complete")
    return urgent

if __name__ == "__main__":
    urgent_messages = main()
    # Exit with count of urgent messages for shell scripts
    exit(len(urgent_messages))
