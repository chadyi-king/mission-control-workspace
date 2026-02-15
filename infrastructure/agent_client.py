#!/usr/bin/env python3
"""
Agent Client Library
Simple interface for agents to use the infrastructure
"""

import asyncio
import websockets
import json
import requests
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HUB_URL = 'ws://localhost:9000'
TOOL_BRIDGE_URL = 'http://localhost:9001'

class AgentClient:
    """Client for agents to communicate with infrastructure"""
    
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.ws = None
        self.connected = False
        
    async def connect(self):
        """Connect to WebSocket hub"""
        try:
            self.ws = await websockets.connect(HUB_URL)
            
            # Register
            await self.ws.send(json.dumps({
                'type': 'register',
                'agent_id': self.agent_id
            }))
            
            self.connected = True
            logger.info(f"[{self.agent_id}] Connected to hub")
            
            # Start listener
            asyncio.create_task(self._listen())
            
        except Exception as e:
            logger.error(f"[{self.agent_id}] Connection failed: {e}")
            self.connected = False
    
    async def _listen(self):
        """Listen for incoming messages"""
        try:
            async for message in self.ws:
                data = json.loads(message)
                await self._handle_message(data)
        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"[{self.agent_id}] Connection closed")
            self.connected = False
    
    async def _handle_message(self, data):
        """Handle incoming message"""
        logger.info(f"[{self.agent_id}] Received: {data.get('type')} from {data.get('from')}")
        
        # Subclasses override this
        pass
    
    async def broadcast(self, msg_type, payload):
        """Broadcast message to all agents"""
        if not self.connected:
            logger.warning(f"[{self.agent_id}] Not connected")
            return
            
        await self.ws.send(json.dumps({
            'type': msg_type,
            'target': 'broadcast',
            'payload': payload
        }))
    
    async def send_to(self, target_agent, msg_type, payload):
        """Send message to specific agent"""
        if not self.connected:
            logger.warning(f"[{self.agent_id}] Not connected")
            return
            
        await self.ws.send(json.dumps({
            'type': msg_type,
            'target': f'agent:{target_agent}',
            'payload': payload
        }))
    
    # Tool Bridge Methods
    
    def exec(self, command, timeout=30):
        """Execute shell command"""
        try:
            resp = requests.post(f'{TOOL_BRIDGE_URL}/exec', json={
                'agent_id': self.agent_id,
                'command': command,
                'timeout': timeout
            })
            return resp.json()
        except Exception as e:
            return {'error': str(e)}
    
    def file_write(self, path, content):
        """Write file to workspace"""
        try:
            resp = requests.post(f'{TOOL_BRIDGE_URL}/file/write', json={
                'agent_id': self.agent_id,
                'path': path,
                'content': content
            })
            return resp.json()
        except Exception as e:
            return {'error': str(e)}
    
    def file_read(self, path):
        """Read file from workspace"""
        try:
            resp = requests.post(f'{TOOL_BRIDGE_URL}/file/read', json={
                'agent_id': self.agent_id,
                'path': path
            })
            return resp.json()
        except Exception as e:
            return {'error': str(e)}
    
    def image_gen(self, prompt, size='1024x1024'):
        """Generate image"""
        try:
            resp = requests.post(f'{TOOL_BRIDGE_URL}/image/gen', json={
                'agent_id': self.agent_id,
                'prompt': prompt,
                'size': size
            })
            return resp.json()
        except Exception as e:
            return {'error': str(e)}
    
    def health_check(self):
        """Check tool bridge health"""
        try:
            resp = requests.get(f'{TOOL_BRIDGE_URL}/health')
            return resp.json()
        except Exception as e:
            return {'error': str(e)}

# Example usage
if __name__ == '__main__':
    async def test():
        client = AgentClient('test-agent')
        await client.connect()
        
        # Test exec
        result = client.exec('echo "Hello from agent"')
        print(f"Exec result: {result}")
        
        # Test file write
        result = client.file_write('test-output.txt', 'Test content from agent client')
        print(f"File write: {result}")
        
        await asyncio.sleep(2)
    
    asyncio.run(test())
