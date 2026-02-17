# Redis Communication Module for Helios-Chad
# Supports both TCP (redis-py) and REST (upstash) protocols

import json
import time
import threading
import requests
from typing import Callable, Dict, Any, Optional

class RedisComm:
    """Real-time communication via Upstash Redis (REST API)"""
    
    def __init__(self, node_name: str = "helios", use_rest: bool = True):
        self.node_name = node_name
        self.use_rest = use_rest
        
        # REST API config
        self.rest_url = "https://national-gar-36005.upstash.io"
        self.rest_token = "AYylAAIncDJkMDBlNjYyOGNjZWM0NDk4ODJlODgxOTVjZjllNzc2N3AyMzYwMDU"
        
        # TCP config (fallback)
        self.redis_client = None
        self.pubsub = None
        
        self.running = False
        self.handlers: Dict[str, Callable] = {}
        self.poll_thread = None
        
    def _rest_request(self, command: str, *args) -> Any:
        """Make REST API request to Upstash Redis"""
        url = f"{self.rest_url}/{command}"
        headers = {
            "Authorization": f"Bearer {self.rest_token}",
            "Content-Type": "application/json"
        }
        
        # Build query string from args
        query_params = "/".join(str(arg) for arg in args)
        if query_params:
            url = f"{url}/{query_params}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"REST error: {e}")
            return None
    
    def _rest_publish(self, channel: str, message: str) -> bool:
        """Publish message via REST API"""
        url = f"{self.rest_url}/publish/{channel}/{message}"
        headers = {"Authorization": f"Bearer {self.rest_token}"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Publish error: {e}")
            return False
    
 def send(self, target: str, message_type: str, data: Any) -> bool:
        """Send message to target node"""
        channel = f"{self.node_name}→{target}"
        message = {
            "from": self.node_name,
            "to": target,
            "type": message_type,
            "timestamp": time.time(),
            "data": data
        }
        
        if self.use_rest:
            # Use REST API
            return self._rest_publish(channel, json.dumps(message))
        else:
            # Use TCP (redis-py)
            try:
                self.redis_client.publish(channel, json.dumps(message))
                return True
            except Exception as e:
                print(f"Send error: {e}")
                return False
    
    def broadcast(self, message_type: str, data: Any) -> bool:
        """Broadcast to all nodes"""
        message = {
            "from": self.node_name,
            "type": message_type,
            "timestamp": time.time(),
            "data": data
        }
        
        if self.use_rest:
            return self._rest_publish("broadcast", json.dumps(message))
        else:
            try:
                self.redis_client.publish("broadcast", json.dumps(message))
                return True
            except Exception as e:
                print(f"Broadcast error: {e}")
                return False
    
    def on(self, message_type: str, handler: Callable):
        """Register message handler"""
        self.handlers[message_type] = handler
        
    def start_listening(self, sources: list = None):
        """Start listening for messages (REST polling mode)"""
        if sources is None:
            sources = ["chad", "broadcast"]
        
        self.running = True
        self.subscribed_channels = sources
        
        def poll():
            """Poll for messages via REST API"""
            while self.running:
                try:
                    for source in self.subscribed_channels:
                        if source == "broadcast":
                            channel = "broadcast"
                        else:
                            channel = f"{source}→{self.node_name}"
                        
                        # Get messages from list (RPOP)
                        result = self._rest_request("lpop", f"channel:{channel}")
                        if result and result.get("result"):
                            try:
                                data = json.loads(result["result"])
                                msg_type = data.get('type', 'unknown')
                                if msg_type in self.handlers:
                                    self.handlers[msg_type](data)
                                else:
                                    print(f"[{self.node_name}] Unhandled: {data}")
                            except json.JSONDecodeError:
                                pass
                    
                    time.sleep(0.5)  # Poll every 500ms
                except Exception as e:
                    print(f"Poll error: {e}")
                    time.sleep(1)
        
        self.poll_thread = threading.Thread(target=poll, daemon=True)
        self.poll_thread.start()
        print(f"[{self.node_name}] Listening on: {sources}")
        
    def stop(self):
        """Stop listening"""
        self.running = False
        if self.pubsub:
            self.pubsub.unsubscribe()
            self.pubsub.close()

# Example usage
if __name__ == "__main__":
    import sys
    
    node = sys.argv[1] if len(sys.argv) > 1 else "helios"
    comm = RedisComm(node_name=node, use_rest=True)
    
    # Register handlers
    def on_task(data):
        print(f"\n📥 Task from {data['from']}: {data['data']}")
        # Acknowledge
        comm.send(data['from'], "ack", {"task_id": data['data'].get('id'), "status": "received"})
    
    def on_ack(data):
        print(f"\n✅ Ack from {data['from']}: {data['data']}")
    
    def on_test(data):
        print(f"\n🧪 Test from {data['from']}: {data['data']}")
    
    comm.on("task", on_task)
    comm.on("ack", on_ack)
    comm.on("test", on_test)
    
    # Start listening
    targets = ["helios", "chad", "broadcast"] if node == "chad" else ["chad", "broadcast"]
    comm.start_listening(targets)
    
    print(f"\n🚀 {node.upper()} ready!")
    print("Commands: send <target> <type> <message> | broadcast <message> | quit")
    
    # Interactive mode
    try:
        while True:
            cmd = input(f"\n{node}> ").strip()
            if cmd == "quit":
                break
            elif cmd.startswith("send "):
                parts = cmd.split(" ", 3)
                if len(parts) >= 4:
                    _, target, msg_type, msg = parts
                    comm.send(target, msg_type, {"message": msg})
                    print(f"📤 Sent to {target}")
            elif cmd.startswith("broadcast "):
                msg = cmd[10:]
                comm.broadcast("message", {"text": msg})
                print(f"📢 Broadcasted")
            else:
                print("Unknown command")
    except KeyboardInterrupt:
        pass
    finally:
        comm.stop()
        print(f"\n👋 {node} stopped")
