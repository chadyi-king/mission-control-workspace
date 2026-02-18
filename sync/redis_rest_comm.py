# Upstash REST API Communication Module for Helios-Chad
# Uses HTTP REST API with tiered priority system (urgent/normal/low)

import urllib.request
import urllib.parse
import json
import time

UPSTASH_REST_URL = "https://national-gar-36005.upstash.io"
UPSTASH_REST_TOKEN = "AYylAAIncDI4Y2EwM2YyNWM4ZDk0N2M4OTJmMmE3ODFiYjEwYWYzYnAyMzYwMDU"

# Priority channels
CHANNELS = {
    'urgent': 'chad→helios-urgent',
    'normal': 'chad→helios',
    'low': 'chad→helios-low'
}

RECEIVE_CHANNELS = {
    'urgent': 'helios→chad-urgent',
    'normal': 'helios→chad',
    'low': 'helios→chad-low'
}

class RedisRestComm:
    """Redis communication via Upstash REST API with priority levels"""
    
    def __init__(self, node_name="chad"):
        self.node_name = node_name
        self.base_url = UPSTASH_REST_URL
        self.token = UPSTASH_REST_TOKEN
        
    def _call(self, command, *args):
        """Execute Redis command via REST API"""
        encoded_args = [urllib.parse.quote(str(arg), safe='') for arg in args]
        path = "/".join([command] + encoded_args)
        
        url = f"{self.base_url}/{path}"
        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {self.token}"},
            method="GET"
        )
        
        try:
            response = urllib.request.urlopen(req, timeout=10)
            return json.loads(response.read().decode())
        except Exception as e:
            print(f"Redis REST error: {e}")
            return None
    
    def send(self, target, message_type, data, priority='normal'):
        """Send message with priority level (urgent/normal/low)"""
        if priority == 'urgent':
            channel = f"{self.node_name}→{target}-urgent"
        elif priority == 'low':
            channel = f"{self.node_name}→{target}-low"
        else:
            channel = f"{self.node_name}→{target}"
            
        message = {
            "from": self.node_name,
            "to": target,
            "type": message_type,
            "priority": priority,
            "timestamp": time.time(),
            "data": data
        }
        
        message_str = json.dumps(message)
        result = self._call("LPUSH", channel, message_str)
        
        priority_emoji = {"urgent": "🔴", "normal": "🟡", "low": "🟢"}
        print(f"{priority_emoji.get(priority, '🟡')} Sent {priority} message to {target}: {message_type}")
        return result is not None
    
    def receive_by_priority(self, source, priority='normal'):
        """Receive messages by priority level"""
        if priority == 'urgent':
            channel = f"{source}→{self.node_name}-urgent"
        elif priority == 'low':
            channel = f"{source}→{self.node_name}-low"
        else:
            channel = f"{source}→{self.node_name}"
            
        result = self._call("LRANGE", channel, "0", "-1")
        
        if result and 'result' in result:
            messages = result['result']
            parsed = []
            for msg in messages:
                try:
                    parsed.append(json.loads(msg))
                except:
                    parsed.append(msg)
            return parsed
        return []
    
    def receive_all(self, source):
        """Receive all messages grouped by priority"""
        return {
            'urgent': self.receive_by_priority(source, 'urgent'),
            'normal': self.receive_by_priority(source, 'normal'),
            'low': self.receive_by_priority(source, 'low')
        }
    
    def clear_inbox_by_priority(self, source, priority='normal'):
        """Clear inbox by priority"""
        if priority == 'urgent':
            channel = f"{source}→{self.node_name}-urgent"
        elif priority == 'low':
            channel = f"{source}→{self.node_name}-low"
        else:
            channel = f"{source}→{self.node_name}"
        self._call("DEL", channel)
    
    def clear_all_inboxes(self, source):
        """Clear all priority inboxes"""
        for priority in ['urgent', 'normal', 'low']:
            self.clear_inbox_by_priority(source, priority)

# Test function
if __name__ == "__main__":
    comm = RedisRestComm("chad")
    print("Testing REST API with priority levels...")
    
    # Test ping
    result = comm._call("PING")
    print(f"Ping: {result}")
    
    # Test urgent message
    comm.send("helios", "test_urgent", {"message": "Urgent test!"}, priority='urgent')
    
    # Test normal message
    comm.send("helios", "test_normal", {"message": "Normal test"}, priority='normal')
    
    # Test low priority
    comm.send("helios", "test_low", {"message": "Low priority test"}, priority='low')
    
    print("\nMessages sent with priority levels!")
