# Redis Communication Module for Helios-Chad
# Uses TCP connection with TLS for Upstash

import json
import time
import threading
import redis
from typing import Callable, Dict, Any, Optional

class RedisComm:
    """Real-time communication via Upstash Redis (TCP with TLS)"""
    
    def __init__(self, node_name: str = "helios"):
        self.node_name = node_name
        
        # TCP connection with TLS
        self.redis_client = redis.Redis(
            host='national-gar-36005.upstash.io',
            port=6379,
            password='AYylAAIncDJkMDBlNjYyOGNjZWM0NDk4ODJlODgxOTVjZjllNzc2N3AyMzYwMDU',
            username='default',
            ssl=True,
            decode_responses=True
        )
        self.pubsub = None
        
        self.running = False
        self.handlers: Dict[str, Callable] = {}
        self.thread = None
        
    def send(self, target: str, message_type: str, data: Any) -> bool:
        """Send message to target node"""
        try:
            channel = f"{self.node_name}→{target}"
            message = {
                "from": self.node_name,
                "to": target,
                "type": message_type,
                "timestamp": time.time(),
                "data": data
            }
            self.redis_client.publish(channel, json.dumps(message))
            return True
        except Exception as e:
            print(f"[{self.node_name}] Send error: {e}")
            return False
    
    def broadcast(self, message_type: str, data: Any) -> bool:
        """Broadcast to all nodes"""
        try:
            message = {
                "from": self.node_name,
                "type": message_type,
                "timestamp": time.time(),
                "data": data
            }
            self.redis_client.publish("broadcast", json.dumps(message))
            return True
        except Exception as e:
            print(f"[{self.node_name}] Broadcast error: {e}")
            return False
    
    def on(self, message_type: str, handler: Callable):
        """Register message handler"""
        self.handlers[message_type] = handler
        
    def start_listening(self, sources: list = None):
        """Start listening for messages"""
        if sources is None:
            sources = ["chad", "broadcast"]
        
        self.pubsub = self.redis_client.pubsub()
        
        for source in sources:
            if source == "broadcast":
                self.pubsub.subscribe("broadcast")
            else:
                channel = f"{source}→{self.node_name}"
                self.pubsub.subscribe(channel)
        
        self.running = True
        
        def listen():
            for message in self.pubsub.listen():
                if not self.running:
                    break
                if message['type'] == 'message':
                    try:
                        data = json.loads(message['data'])
                        msg_type = data.get('type', 'unknown')
                        if msg_type in self.handlers:
                            self.handlers[msg_type](data)
                        else:
                            print(f"[{self.node_name}] Unhandled: {msg_type}")
                    except json.JSONDecodeError:
                        print(f"[{self.node_name}] Invalid JSON: {message['data']}")
        
        self.thread = threading.Thread(target=listen, daemon=True)
        self.thread.start()
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
    comm = RedisComm(node_name=node)
    
    # Register handlers
    def on_task(data):
        print(f"\n📥 [{node}] Task from {data['from']}: {data['data']}")
        comm.send(data['from'], "ack", {"task_id": data['data'].get('id'), "status": "received"})
    
    def on_ack(data):
        print(f"\n✅ [{node}] Ack from {data['from']}: {data['data']}")
    
    def on_test(data):
        print(f"\n🧪 [{node}] Test from {data['from']}: {data['data']}")
    
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
