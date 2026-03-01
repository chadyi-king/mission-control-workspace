#!/usr/bin/env python3
"""
Fixed Redis Communication for CHAD_YI
Uses dash (-) instead of arrow (→) to match Helios
"""

import urllib.request
import urllib.parse
import json
import time

UPSTASH_REST_URL = "https://national-gar-36005.upstash.io"
UPSTASH_REST_TOKEN = "AYylAAIncDI4Y2EwM2YyNWM4ZDk0N2M4OTJmMmE3ODFiYjEwYWYzYnAyMzYwMDU"

class RedisComm:
    """Redis communication via REST API - FIXED to use dash channels"""
    
    def __init__(self, node_name="chad"):
        self.node_name = node_name
        self.base_url = UPSTASH_REST_URL
        self.token = UPSTASH_REST_TOKEN
        
    def _call(self, command, *args):
        """Execute Redis command via REST API"""
        encoded_args = [urllib.parse.quote(str(arg), safe='') for arg in args]
        path = "/".join([command] + encoded_args)
        url = f"{self.base_url}/{path}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {self.token}"}, method="GET")
        try:
            response = urllib.request.urlopen(req, timeout=10)
            return json.loads(response.read().decode())
        except Exception as e:
            return {"error": str(e)}
    
    def ping(self):
        """Test connection"""
        result = self._call("PING")
        return result and result.get('result') == 'PONG'
    
    def send(self, target, message_type, data, priority='normal'):
        """Send message to target node - USES DASH CHANNELS"""
        # Use DASH instead of ARROW to match Helios
        if priority == 'urgent':
            channel = f"{self.node_name}-{target}-urgent"
        elif priority == 'low':
            channel = f"{self.node_name}-{target}-low"
        else:
            channel = f"{self.node_name}-{target}"
            
        message = {
            "from": self.node_name,
            "to": target,
            "type": message_type,
            "priority": priority,
            "timestamp": time.time(),
            "data": data
        }
        
        result = self._call("LPUSH", channel, json.dumps(message))
        emoji = {"urgent": "🔴", "normal": "🟡", "low": "🟢"}
        print(f"{emoji.get(priority, '🟡')} Sent to {target}: {message_type}")
        return result is not None
    
    def receive(self, source, priority='normal'):
        """Receive messages from source - USES DASH CHANNELS"""
        # Use DASH instead of ARROW to match Helios
        if priority == 'urgent':
            channel = f"{source}-{self.node_name}-urgent"
        elif priority == 'low':
            channel = f"{source}-{self.node_name}-low"
        else:
            channel = f"{source}-{self.node_name}"
            
        result = self._call("LRANGE", channel, "0", "-1")
        
        if result and 'result' in result:
            messages = []
            for msg in result['result']:
                try:
                    messages.append(json.loads(msg))
                except:
                    # Handle plain text messages from Helios
                    messages.append({
                        "type": "plain_text",
                        "raw": msg,
                        "from": source,
                        "timestamp": time.time()
                    })
            return messages
        return []
    
    def receive_all(self, source):
        """Receive all messages grouped by priority"""
        return {
            'urgent': self.receive(source, 'urgent'),
            'normal': self.receive(source, 'normal'),
            'low': self.receive(source, 'low')
        }
    
    def clear_inbox(self, source, priority='normal'):
        """Clear inbox - USES DASH CHANNELS"""
        if priority == 'urgent':
            channel = f"{source}-{self.node_name}-urgent"
        elif priority == 'low':
            channel = f"{source}-{self.node_name}-low"
        else:
            channel = f"{source}-{self.node_name}"
        self._call("DEL", channel)

# Global instance
comm = RedisComm("chad")

if __name__ == "__main__":
    # Test connection
    print("Testing Redis connection...")
    if comm.ping():
        print("✅ Connected to Redis via REST API")
    else:
        print("❌ Connection failed")
        exit(1)
    
    # Check for Helios messages on DASH channels
    print("\nChecking for messages from Helios (DASH channels)...")
    all_messages = comm.receive_all("helios")
    
    total = sum(len(v) for v in all_messages.values())
    if total == 0:
        print("📭 No messages from Helios")
    else:
        for priority, messages in all_messages.items():
            if messages:
                emoji = {"urgent": "🔴", "normal": "🟡", "low": "🟢"}
                print(f"\n{emoji.get(priority, '⚪')} {priority.upper()}: {len(messages)} message(s)")
                for msg in messages:
                    if msg.get('type') == 'plain_text':
                        print(f"   - Plain text: {msg.get('raw', '')[:100]}...")
                    else:
                        print(f"   - {msg.get('type')}: {str(msg.get('data', {}))[:100]}")
        
        # Clear after reading
        comm.clear_inbox("helios")
        print(f"\n✅ Processed {total} message(s)")
