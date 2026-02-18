# Upstash REST API Communication Module for Helios-Chad
# Uses HTTP REST API instead of Redis protocol (works with REST_TOKEN)

import urllib.request
import urllib.parse
import json
import time

UPSTASH_REST_URL = "https://national-gar-36005.upstash.io"
UPSTASH_REST_TOKEN = "AYylAAIncDI4Y2EwM2YyNWM4ZDk0N2M4OTJmMmE3ODFiYjEwYWYzYnAyMzYwMDU"

class RedisRestComm:
    """Redis communication via Upstash REST API"""
    
    def __init__(self, node_name="chad"):
        self.node_name = node_name
        self.base_url = UPSTASH_REST_URL
        self.token = UPSTASH_REST_TOKEN
        
    def _call(self, command, *args):
        """Execute Redis command via REST API"""
        # URL encode all arguments
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
    
    def send(self, target, message_type, data):
        """Send message to target node"""
        channel = f"{self.node_name}→{target}"
        message = {
            "from": self.node_name,
            "to": target,
            "type": message_type,
            "timestamp": time.time(),
            "data": data
        }
        # Store as JSON string (base64 encode if needed for complex data)
        message_str = json.dumps(message)
        result = self._call("LPUSH", channel, message_str)
        return result is not None
    
    def receive(self, source):
        """Receive messages from source node"""
        channel = f"{source}→{self.node_name}"
        result = self._call("LRANGE", channel, "0", "-1")
        
        if result and 'result' in result:
            messages = result['result']
            # Parse JSON messages
            parsed = []
            for msg in messages:
                try:
                    parsed.append(json.loads(msg))
                except:
                    parsed.append(msg)
            return parsed
        return []
    
    def clear_inbox(self, source):
        """Clear messages after processing"""
        channel = f"{source}→{self.node_name}"
        self._call("DEL", channel)

# Test function
if __name__ == "__main__":
    comm = RedisRestComm("chad")
    print("Testing REST API communication...")
    
    # Test ping
    result = comm._call("PING")
    print(f"Ping: {result}")
    
    # Test send
    comm.send("helios", "test", {"message": "Hello via REST API!"})
    print("Message sent to Helios")
    
    # Test receive
    msgs = comm.receive("helios")
    print(f"Messages from Helios: {len(msgs)}")
    
    print("REST API communication ready!")
