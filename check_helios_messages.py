#!/usr/bin/env python3
"""Check Redis for messages from Helios - One-time poll"""

import json
import time
import redis

# Connect to Redis
redis_client = redis.Redis(
    host='national-gar-36005.upstash.io',
    port=6379,
    password='AYylAAIncDJkMDBlNjYyOGNjZWM0NDk4ODJlODgxOTVjZjllNzc2N3AyMzYwMDU',
    username='default',
    ssl=True,
    decode_responses=True
)

# Check connection
try:
    redis_client.ping()
    print("✅ Connected to Redis")
except Exception as e:
    print(f"❌ Redis connection failed: {e}")
    exit(1)

# Subscribe to helios→chad channel
pubsub = redis_client.pubsub()
pubsub.subscribe('helios→chad')

print("📡 Checking for messages from Helios...")

# Wait a moment to get any queued messages
messages = []
timeout = 2  # seconds
start_time = time.time()

while time.time() - start_time < timeout:
    message = pubsub.get_message(timeout=0.5)
    if message and message['type'] == 'message':
        try:
            data = json.loads(message['data'])
            messages.append(data)
            print(f"📥 Received: {data}")
        except json.JSONDecodeError:
            print(f"⚠️ Invalid JSON: {message['data']}")

if not messages:
    print("📭 No messages from Helios")
else:
    print(f"\n📨 Found {len(messages)} message(s) from Helios:")
    for msg in messages:
        print(f"  - Type: {msg.get('type', 'unknown')}")
        print(f"    From: {msg.get('from', 'unknown')}")
        print(f"    Data: {msg.get('data', {})}")
        print(f"    Timestamp: {msg.get('timestamp', 'N/A')}")
        
        # Reply back to Helios
        reply_channel = f"chad→helios"
        reply = {
            "from": "chad",
            "to": "helios",
            "type": "ack",
            "timestamp": time.time(),
            "data": {
                "original_type": msg.get('type'),
                "status": "received",
                "message": "Message received by Chad"
            }
        }
        redis_client.publish(reply_channel, json.dumps(reply))
        print(f"  ✅ Replied to Helios on {reply_channel}\n")

pubsub.unsubscribe()
pubsub.close()
redis_client.close()

# Summary
if messages:
    print(f"\n📊 SUMMARY: Processed {len(messages)} message(s) from Helios, replied to all.")
else:
    print("\n📊 SUMMARY: No messages waiting.")
