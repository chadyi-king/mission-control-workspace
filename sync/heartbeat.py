#!/usr/bin/env python3
"""
Heartbeat System for Helios-Chad Sync
Sends and receives heartbeats to monitor sync health
"""

import json
import time
import socket
import threading
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
HEARTBEAT_PORT = 8765
HEARTBEAT_INTERVAL = 60  # seconds
HEARTBEAT_TIMEOUT = 180  # 3 minutes
LOG_DIR = Path("/root/.openclaw/workspace/logs")
STATE_FILE = Path("/root/.openclaw/workspace/sync/heartbeat_state.json")

# Setup logging
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "heartbeat.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("heartbeat")

class HeartbeatSystem:
    def __init__(self, node_name, peer_host, peer_port=HEARTBEAT_PORT):
        self.node_name = node_name
        self.peer_host = peer_host
        self.peer_port = peer_port
        self.start_time = time.time()
        self.pid = os.getpid()
        self.status = "healthy"
        self.last_peer_heartbeat = None
        self.running = False
        self.lock = threading.Lock()
        
    def get_uptime(self):
        return int(time.time() - self.start_time)
    
    def create_heartbeat(self):
        return {
            "type": "heartbeat",
            "from": self.node_name,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": self.status,
            "pid": self.pid,
            "uptime": self.get_uptime()
        }
    
    def send_heartbeat(self):
        """Send heartbeat to peer"""
        try:
            heartbeat = self.create_heartbeat()
            data = json.dumps(heartbeat).encode('utf-8')
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(5)
            sock.sendto(data, (self.peer_host, self.peer_port))
            logger.info(f"Heartbeat sent to {self.peer_host}:{self.peer_port}")
            
            # Save state
            self.save_state()
            return True
        except Exception as e:
            logger.error(f"Failed to send heartbeat: {e}")
            return False
        finally:
            try:
                sock.close()
            except:
                pass
    
    def receive_heartbeat(self):
        """Listen for incoming heartbeats"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            sock.bind(('0.0.0.0', self.peer_port))
            logger.info(f"Listening for heartbeats on port {self.peer_port}")
            
            while self.running:
                try:
                    sock.settimeout(1)
                    data, addr = sock.recvfrom(1024)
                    
                    try:
                        heartbeat = json.loads(data.decode('utf-8'))
                        if heartbeat.get("type") == "heartbeat":
                            with self.lock:
                                self.last_peer_heartbeat = datetime.utcnow()
                            
                            logger.info(f"Received heartbeat from {heartbeat.get('from')} "
                                      f"(status: {heartbeat.get('status')}, "
                                      f"uptime: {heartbeat.get('uptime')}s)")
                            
                            # Save received heartbeat
                            self.save_peer_state(heartbeat)
                    except json.JSONDecodeError:
                        logger.warning(f"Received invalid heartbeat data from {addr}")
                        
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"Error receiving heartbeat: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to bind heartbeat socket: {e}")
        finally:
            sock.close()
    
    def save_state(self):
        """Save local heartbeat state"""
        try:
            state = {
                "node": self.node_name,
                "last_sent": datetime.utcnow().isoformat() + "Z",
                "status": self.status,
                "uptime": self.get_uptime()
            }
            STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(STATE_FILE, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")
    
    def save_peer_state(self, heartbeat):
        """Save peer heartbeat state"""
        try:
            peer_file = STATE_FILE.parent / f"peer_{heartbeat.get('from')}_state.json"
            with open(peer_file, 'w') as f:
                json.dump({
                    "received_at": datetime.utcnow().isoformat() + "Z",
                    "heartbeat": heartbeat
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save peer state: {e}")
    
    def check_peer_health(self):
        """Check if peer is healthy based on last heartbeat"""
        with self.lock:
            if self.last_peer_heartbeat is None:
                return "unknown"
            
            elapsed = (datetime.utcnow() - self.last_peer_heartbeat).total_seconds()
            
            if elapsed > HEARTBEAT_TIMEOUT:
                return "down"
            elif elapsed > HEARTBEAT_INTERVAL * 2:
                return "degraded"
            else:
                return "healthy"
    
    def sender_loop(self):
        """Main sender loop"""
        while self.running:
            self.send_heartbeat()
            time.sleep(HEARTBEAT_INTERVAL)
    
    def start(self):
        """Start the heartbeat system"""
        self.running = True
        
        # Start receiver thread
        receiver_thread = threading.Thread(target=self.receive_heartbeat, daemon=True)
        receiver_thread.start()
        
        # Start sender thread
        sender_thread = threading.Thread(target=self.sender_loop, daemon=True)
        sender_thread.start()
        
        logger.info(f"Heartbeat system started for {self.node_name}")
        
        return receiver_thread, sender_thread
    
    def stop(self):
        """Stop the heartbeat system"""
        self.running = False
        logger.info("Heartbeat system stopped")


def get_peer_for_node(node_name):
    """Get the peer host for a given node"""
    # Map of node names to their peer hosts
    peers = {
        "helios": "chad",  # Helios sends to Chad
        "chad": "helios"   # Chad sends to Helios
    }
    
    peer = peers.get(node_name)
    if not peer:
        raise ValueError(f"Unknown node: {node_name}")
    
    # Resolve peer to IP (can be overridden with env var)
    peer_host = os.environ.get(f"{peer.upper()}_HOST", peer)
    return peer_host


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Heartbeat System")
    parser.add_argument("--node", required=True, choices=["helios", "chad"],
                       help="Node name (helios or chad)")
    parser.add_argument("--peer-host", help="Peer host (auto-detected if not specified)")
    parser.add_argument("--port", type=int, default=HEARTBEAT_PORT,
                       help=f"Port to use (default: {HEARTBEAT_PORT})")
    
    args = parser.parse_args()
    
    peer_host = args.peer_host or get_peer_for_node(args.node)
    
    hb = HeartbeatSystem(args.node, peer_host, args.port)
    
    try:
        hb.start()
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        hb.stop()


if __name__ == "__main__":
    main()
