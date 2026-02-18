#!/usr/bin/env python3
"""Check Redis for messages from Helios and report results"""

import json
import time
import redis

# Redis connection
redis_client = redis.Redis(
    host='national-gar-36005.upstash.io',
    port=6379,
    password='AYylAAIncDJkMDBlNjYyOGNjZWM0NDk4ODJlODgxOTVjZjllNzc2N3AyMzYwMDU',
    username='default',
    ssl=True,
    decode_responses=True
)

# Subscribe to helios→chad channel
pubsub = redis_client.pubsub()
channel = 'helios→chad'
pubsub.subscribe(channel)

print(f"[Chad] Checking Redis channel: {channel}")

# Poll for messages with a short timeout
messages_found = []
reply_count = 0

# Listen for messages for up to 3 seconds
timeout = 3.0
start_time = time.time()

while time.time() - start_time < timeout:
    message = pubsub.get_message(timeout=0.5)
    if message and message['type'] == 'message':
        try:
            data = json.loads(message['data'])
            msg_from = data.get('from', 'unknown')
            msg_type = data.get('type', 'unknown')
            msg_data = data.get('data', {})
            msg_timestamp = data.get('timestamp', 0)
            
            messages_found.append({
                'from': msg_from,
                'type': msg_type,
                'data': msg_data,
                'timestamp': msg_timestamp
            })
            
            # Reply back to Helios
            reply_channel = f"chad→helios"
            reply = {
                "from": "chad",
                "to": "helios",
                "type": "ack",
                "in_reply_to": msg_type,
                "timestamp": time.time(),
                "data": {
                    "status": "received",
                    "received_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "original": msg_data
                }
            }
            redis_client.publish(reply_channel, json.dumps(reply))
            reply_count += 1
            print(f"[Chad] Received: {msg_type} from {msg_from}")
            print(f"[Chad] Replied: ack to {msg_from}")
            
        except json.JSONDecodeError:
            print(f"[Chad] Invalid JSON received")
    elif message is None:
        # No message available, continue polling
        pass

# Clean up
pubsub.unsubscribe()
pubsub.close()

# Report results
if messages_found:
    print(f"\n{'='*50}")
    print(f"REDIS CHECK SUMMARY")
    print(f"{'='*50}")
    print(f"Messages received from Helios: {len(messages_found)}")
    print(f"Replies sent to Helios: {reply_count}")
    print(f"\nDetails:")
    for i, msg in enumerate(messages_found, 1):
        print(f"  {i}. Type: '{msg['type']}'")
        print(f"     Data: {json.dumps(msg['data'], indent=2)}")
        print(f"     Time: {time.strftime('%H:%M:%S', time.localtime(msg['timestamp']))}")
    print(f"{'='*50}")
else:
    # Silent when no messages (as instructed)
    pass
