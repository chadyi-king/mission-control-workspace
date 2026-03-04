#!/usr/bin/env python3
"""
ACP Client Library for Python Agents
Simplifies ACP protocol for agent integration
"""

import json
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ACPMessage:
    """Represents an ACP protocol message"""
    method: str
    params: Dict[str, Any]
    msg_id: int
    
    def to_json(self) -> str:
        return json.dumps({
            "jsonrpc": "2.0",
            "method": self.method,
            "params": self.params,
            "id": self.msg_id
        })

@dataclass
class ACPResponse:
    """Represents an ACP response"""
    success: bool
    result: Optional[Dict] = None
    error: Optional[Dict] = None
    msg_id: Optional[int] = None

class ACPClient:
    """ACP Client for agent communication"""
    
    def __init__(self, agent_name: str, session_label: str = None):
        self.agent_name = agent_name
        self.session_label = session_label or agent_name
        self.msg_counter = 0
        self.connected = False
        self.capabilities = {}
        
    def _next_id(self) -> int:
        self.msg_counter += 1
        return self.msg_counter
    
    def initialize(self) -> ACPResponse:
        """Initialize connection to ACP gateway"""
        msg = ACPMessage(
            method="initialize",
            params={"protocolVersion": 1, "agent": self.agent_name},
            msg_id=self._next_id()
        )
        
        result = self._send_raw(msg.to_json())
        if result.success:
            self.connected = True
            self.capabilities = result.result.get("agentCapabilities", {})
        return result
    
    def send_message(self, to_agent: str, content: str, priority: str = "normal") -> ACPResponse:
        """Send a message to another agent"""
        msg = ACPMessage(
            method="agents/send",
            params={
                "to": to_agent,
                "from": self.agent_name,
                "content": content,
                "priority": priority,
                "timestamp": datetime.now().isoformat()
            },
            msg_id=self._next_id()
        )
        return self._send_raw(msg.to_json())
    
    def receive_messages(self) -> list:
        """Check for incoming messages"""
        msg = ACPMessage(
            method="agents/receive",
            params={"agent": self.agent_name},
            msg_id=self._next_id()
        )
        result = self._send_raw(msg.to_json())
        if result.success:
            return result.result.get("messages", [])
        return []
    
    def register_capability(self, capability: str, handler: Callable):
        """Register a capability handler"""
        pass  # For future use
    
    def _send_raw(self, json_str: str) -> ACPResponse:
        """Send raw JSON-RPC to ACP gateway via openclaw CLI"""
        try:
            # Create temp file for message
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write(json_str)
                msg_file = f.name
            
            # Call openclaw acp
            result = subprocess.run(
                ["openclaw", "acp", "--session-label", self.session_label],
                input=json_str,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Parse response
            output = result.stdout.strip()
            if not output:
                return ACPResponse(success=False, error={"message": "No response"})
            
            # Find JSON in output (may have warnings before)
            for line in output.split('\n'):
                line = line.strip()
                if line.startswith('{'):
                    try:
                        data = json.loads(line)
                        if "error" in data:
                            return ACPResponse(
                                success=False,
                                error=data["error"],
                                msg_id=data.get("id")
                            )
                        return ACPResponse(
                            success=True,
                            result=data.get("result"),
                            msg_id=data.get("id")
                        )
                    except json.JSONDecodeError:
                        continue
            
            return ACPResponse(success=False, error={"message": "Invalid response"})
            
        except subprocess.TimeoutExpired:
            return ACPResponse(success=False, error={"message": "Timeout"})
        except Exception as e:
            return ACPResponse(success=False, error={"message": str(e)})
        finally:
            # Cleanup
            try:
                os.unlink(msg_file)
            except:
                pass

class FileACPBridge:
    """
    Bridge between file-based agents and ACP
    Allows gradual migration - agents write files, this bridges to ACP
    """
    
    def __init__(self, agent_name: str, inbox_path: Path, outbox_path: Path):
        self.agent_name = agent_name
        self.inbox = inbox_path
        self.outbox = outbox_path
        self.acp = ACPClient(agent_name)
        
    def poll_and_bridge(self):
        """Poll file inbox and bridge to ACP"""
        # Check file inbox
        for file in self.inbox.glob("*.md"):
            content = file.read_text()
            
            # Send via ACP
            result = self.acp.send_message(
                to_agent="chad-yi",
                content=content,
                priority="normal"
            )
            
            if result.success:
                # Archive file
                archive = self.inbox / "archive"
                archive.mkdir(exist_ok=True)
                file.rename(archive / file.name)
                
    def receive_to_files(self):
        """Receive ACP messages and write to file outbox"""
        messages = self.acp.receive_messages()
        
        for msg in messages:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            filename = f"acp-msg-{timestamp}.md"
            
            content = f"""# ACP Message from {msg.get('from', 'unknown')}

{msg.get('content', '')}

---
*Received via ACP at {msg.get('timestamp', 'unknown')}*
"""
            (self.outbox / filename).write_text(content)

# Convenience function
def create_agent(agent_name: str) -> ACPClient:
    """Create and initialize an ACP agent"""
    client = ACPClient(agent_name)
    response = client.initialize()
    if response.success:
        print(f"[ACP] {agent_name} connected successfully")
    else:
        print(f"[ACP] {agent_name} connection failed: {response.error}")
    return client
