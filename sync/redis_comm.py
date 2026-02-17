# Redis Communication Module for Helios-Chad
# Real-time messaging via Upstash Redis

import redis
import json
import os
import threading
import time
from typing import Callable, Dict, Any

class RedisComm:
    """Real-time communication via Upstash Redis"""
    
    def __init__(self, node_name: str = "helios"):
        self.node_name = node_name
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
            print(f"Send error: {e}")
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
            print(f"Broadcast error: {e}")
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
                self.pubsub.subscribe(f"{source}→{self.node_name}")
        
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
                            print(f"Unhandled message: {data}")
                    except json.JSONDecodeError:
                        print(f"Invalid JSON: {message['data']}")
        
        self.thread = threading.Thread(target=listen, daemon=True)
        self.thread.start()
        print(f"Listening on channels: {sources}")
        
    def stop(self):
        """Stop listening"""
        self.running = False
        if self.pubsub:
            self.pubsub.unsubscribe()
            self.pubsub.close()

# Example usage
if __name__ == "__main__":
    comm = RedisComm(node_name="helios")
    
    # Register handlers
    def on_task(data):
        print(f"Received task: {data}")
        # Process task...
        comm.send("chad", "ack", {"task_id": data['data'].get('id')})
    
    def on_heartbeat(data):
        print(f"Heartbeat from {data['from']}")
    
    comm.on("task", on_task)
    comm.on("heartbeat", on_heartbeat)
    
    # Start listening
    comm.start_listening(["chad", "broadcast"])
    
    # Send test message
    comm.send("chad", "test", {"message": "Hello from Helios!"})
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        comm.stop()
