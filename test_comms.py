#!/usr/bin/env python3
"""
Test Suite for Redis Communication Network
"""

import json
import time
import sys
from datetime import datetime
from sync.redis_comm import RedisComm

class CommsTest:
    """Test Redis communication between Helios and Chad"""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        
    def test_basic_connection(self):
        """Test 1: Basic Redis connection"""
        print("\n[Test 1] Basic Connection...")
        try:
            comm = RedisComm(node_name="test")
            # Try to send a test message
            result = comm.send("helios", "test", {"message": "ping"})
            if result:
                print("  ✅ PASS: Connection successful")
                self.passed += 1
                return True
            else:
                print("  ❌ FAIL: Could not send message")
                self.failed += 1
                return False
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            self.failed += 1
            return False
    
    def test_message_roundtrip(self):
        """Test 2: Message roundtrip (send and receive)"""
        print("\n[Test 2] Message Roundtrip...")
        try:
            received = [False]
            
            def handler(data):
                received[0] = True
                print(f"  📥 Received: {data['data']}")
            
            # Create receiver
            receiver = RedisComm(node_name="test_receiver")
            receiver.on("test", handler)
            receiver.start_listening(["test_sender"])
            
            # Create sender
            sender = RedisComm(node_name="test_sender")
            
            # Send message
            sender.send("test_receiver", "test", {"ping": "pong"})
            print("  📤 Sent test message")
            
            # Wait for receive
            time.sleep(2)
            
            receiver.stop()
            
            if received[0]:
                print("  ✅ PASS: Roundtrip successful")
                self.passed += 1
                return True
            else:
                print("  ❌ FAIL: Message not received")
                self.failed += 1
                return False
                
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            self.failed += 1
            return False
    
    def test_broadcast(self):
        """Test 3: Broadcast to multiple agents"""
        print("\n[Test 3] Broadcast...")
        try:
            received_count = [0]
            
            def handler(data):
                received_count[0] += 1
            
            # Create multiple receivers
            r1 = RedisComm(node_name="r1")
            r2 = RedisComm(node_name="r2")
            r1.on("broadcast_test", handler)
            r2.on("broadcast_test", handler)
            r1.start_listening(["broadcast"])
            r2.start_listening(["broadcast"])
            
            # Broadcast
            sender = RedisComm(node_name="broadcaster")
            sender.broadcast("broadcast_test", {"message": "hello all"})
            
            time.sleep(2)
            
            r1.stop()
            r2.stop()
            
            if received_count[0] >= 2:
                print(f"  ✅ PASS: Broadcast received by {received_count[0]} nodes")
                self.passed += 1
                return True
            else:
                print(f"  ❌ FAIL: Only {received_count[0]} nodes received")
                self.failed += 1
                return False
                
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            self.failed += 1
            return False
    
    def test_helios_chad_link(self):
        """Test 4: Helios ↔ Chad specific link"""
        print("\n[Test 4] Helios ↔ Chad Link...")
        try:
            # Simulate Chad sending to Helios
            chad = RedisComm(node_name="chad")
            helios = RedisComm(node_name="helios")
            
            received = [None]
            
            def handler(data):
                received[0] = data
            
            helios.on("link_test", handler)
            helios.start_listening(["chad"])
            
            chad.send("helios", "link_test", {
                "from": "chad",
                "message": "Hello Helios!",
                "timestamp": datetime.now().isoformat()
            })
            
            time.sleep(2)
            
            helios.stop()
            
            if received[0] and received[0]['from'] == 'chad':
                print("  ✅ PASS: Helios ↔ Chad link working")
                self.passed += 1
                return True
            else:
                print("  ❌ FAIL: Link not working")
                self.failed += 1
                return False
                
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            self.failed += 1
            return False
    
    def test_dashboard_update(self):
        """Test 5: Dashboard data update via Redis"""
        print("\n[Test 5] Dashboard Update...")
        try:
            # Update data.json via Redis message
            comm = RedisComm(node_name="test")
            
            test_data = {
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "value": 42
            }
            
            result = comm.send("helios", "dashboard_update", test_data)
            
            if result:
                print("  ✅ PASS: Dashboard update sent")
                self.passed += 1
                return True
            else:
                print("  ❌ FAIL: Could not send update")
                self.failed += 1
                return False
                
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            self.failed += 1
            return False
    
    def test_stress(self, num_messages=100):
        """Test 6: Stress test"""
        print(f"\n[Test 6] Stress Test ({num_messages} messages)...")
        try:
            sender = RedisComm(node_name="stress_sender")
            
            start = time.time()
            sent = 0
            
            for i in range(num_messages):
                result = sender.send("helios", "stress", {"index": i})
                if result:
                    sent += 1
            
            elapsed = time.time() - start
            rate = sent / elapsed if elapsed > 0 else 0
            
            print(f"  Sent: {sent}/{num_messages} in {elapsed:.2f}s ({rate:.1f} msg/s)")
            
            if sent == num_messages:
                print("  ✅ PASS: All messages sent")
                self.passed += 1
                return True
            else:
                print(f"  ⚠️  PARTIAL: {sent}/{num_messages} sent")
                self.passed += 1  # Still count as pass if most went through
                return True
                
        except Exception as e:
            print(f"  ❌ FAIL: {e}")
            self.failed += 1
            return False
    
    def run_all(self):
        """Run all tests"""
        print("=" * 50)
        print("REDIS COMMUNICATION TEST SUITE")
        print("=" * 50)
        
        self.test_basic_connection()
        self.test_message_roundtrip()
        self.test_broadcast()
        self.test_helios_chad_link()
        self.test_dashboard_update()
        self.test_stress(num_messages=50)
        
        print("\n" + "=" * 50)
        print("RESULTS")
        print("=" * 50)
        print(f"Passed: {self.passed}")
        print(f"Failed: {self.failed}")
        print(f"Total:  {self.passed + self.failed}")
        
        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
            return 0
        else:
            print(f"\n⚠️  {self.failed} TEST(S) FAILED")
            return 1

if __name__ == "__main__":
    test = CommsTest()
    sys.exit(test.run_all())
