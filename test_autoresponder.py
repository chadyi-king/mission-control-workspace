#!/usr/bin/env python3
"""Quick test of auto-responder"""
import sys
sys.path.insert(0, '/root/.openclaw/workspace/mission-control-workspace')
from sync.redis_comm import RedisComm
import time

# Create test client
comm = RedisComm(node_name="test_client")

# Send ping to helios
print("Sending ping to helios...")
comm.send("helios", "ping", {"test": True, "time": time.time()})

# Wait a moment
time.sleep(2)

# Send status request
print("Sending status request to helios...")
comm.send("helios", "status_request", {})

# Wait
time.sleep(2)

print("Test complete. Check autoresponder.log for responses.")
comm.stop()
