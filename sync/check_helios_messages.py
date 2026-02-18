#!/usr/bin/env python3
"""
Check Redis for messages from Helios (helios→chad channel)
Non-blocking check for cron job execution
"""

import json
import time
import redis

def main():
    # Connect to Redis
    redis_client = redis.Redis(
        host='national-gar-36005.upstash.io',
        port=6379,
        password='AYylAAIncDJkMDBlNjYyOGNjZWM0NDk4ODJlODgxOTVjZjllNzc2N3AyMzYwMDU',
        username='default',
        ssl=True,
        decode_responses=True
    )
    
    # Test connection
    try:
        redis_client.ping()
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return
    
    # Check for pending messages using pubsub with timeout
    pubsub = redis_client.pubsub()
    pubsub.subscribe('helios→chad')
    
    messages = []
    start_time = time.time()
    
    # Non-blocking check - try to get messages for up to 2 seconds
    while time.time() - start_time < 2:
        message = pubsub.get_message(timeout=0.5)
        if message and message['type'] == 'message':
            try:
                data = json.loads(message['data'])
                messages.append(data)
            except json.JSONDecodeError:
                pass
        elif message is None:
            # No more messages waiting
            break
    
    pubsub.unsubscribe()
    pubsub.close()
    
    if not messages:
        # No messages - stay silent (no output)
        return
    
    # Process messages and reply
    results = []
    
    for msg in messages:
        msg_from = msg.get('from', 'unknown')
        msg_type = msg.get('type', 'unknown')
        msg_data = msg.get('data', {})
        msg_ts = msg.get('timestamp', 0)
        
        # What Helios said
        helios_said = f"[{msg_type}] {msg_data}"
        
        # Craft reply based on message type
        reply_data = {}
        if msg_type == 'ping':
            reply_data = {"status": "pong", "received_at": time.time()}
        elif msg_type == 'task':
            reply_data = {"task_id": msg_data.get('id'), "status": "acknowledged", "by": "chad"}
        elif msg_type == 'status_check':
            reply_data = {"status": "online", "timestamp": time.time()}
        else:
            reply_data = {"status": "received", "type": msg_type}
        
        # Send reply back to Helios
        reply_channel = "chad→helios"
        reply_msg = {
            "from": "chad",
            "to": "helios",
            "type": f"ack_{msg_type}",
            "timestamp": time.time(),
            "data": reply_data,
            "in_reply_to": msg.get('timestamp')
        }
        
        redis_client.publish(reply_channel, json.dumps(reply_msg))
        
        results.append({
            'from': msg_from,
            'type': msg_type,
            'received': helios_said,
            'replied': reply_data
        })
    
    # Report to user
    print(f"📡 Redis Bridge Check - {time.strftime('%H:%M:%S')}")
    print(f"   Found {len(results)} message(s) from Helios:\n")
    
    for i, r in enumerate(results, 1):
        print(f"   {i}. Helios said: [{r['type']}] {r['received']}")
        print(f"      ↳ Replied: {r['replied']}\n")
    
    print("   ✅ All messages processed and replies sent.")

if __name__ == "__main__":
    main()
