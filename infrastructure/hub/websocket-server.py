#!/usr/bin/env python3
"""
Agent Communication Hub
WebSocket server for real-time agent messaging
"""

import asyncio
import websockets
import json
import logging
from datetime import datetime
from collections import defaultdict

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentHub:
    def __init__(self):
        self.agents = {}  # websocket -> agent_id
        self.channels = defaultdict(set)  # channel -> set of websockets
        self.message_history = []  # Last 100 messages
        
    async def register(self, websocket, agent_id):
        """Register new agent connection"""
        self.agents[websocket] = agent_id
        self.channels['broadcast'].add(websocket)
        self.channels[f'agent:{agent_id}'].add(websocket)
        
        logger.info(f"Agent {agent_id} connected")
        
        # Announce to all agents
        await self.broadcast({
            'type': 'agent_joined',
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat(),
            'active_agents': len(self.agents)
        })
        
    async def unregister(self, websocket):
        """Unregister agent connection"""
        agent_id = self.agents.get(websocket, 'unknown')
        
        if websocket in self.agents:
            del self.agents[websocket]
            
        # Remove from all channels
        for channel in self.channels.values():
            channel.discard(websocket)
            
        logger.info(f"Agent {agent_id} disconnected")
        
        await self.broadcast({
            'type': 'agent_left',
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat(),
            'active_agents': len(self.agents)
        })
        
    async def broadcast(self, message):
        """Send message to all connected agents"""
        if self.channels['broadcast']:
            message_json = json.dumps(message)
            await asyncio.gather(
                *[ws.send(message_json) for ws in self.channels['broadcast']],
                return_exceptions=True
            )
            
        # Store in history
        self.message_history.append({
            'timestamp': datetime.now().isoformat(),
            'channel': 'broadcast',
            'message': message
        })
        # Keep only last 100
        self.message_history = self.message_history[-100:]
        
    async def send_to_agent(self, agent_id, message):
        """Send message to specific agent"""
        channel = f'agent:{agent_id}'
        if channel in self.channels:
            message_json = json.dumps(message)
            await asyncio.gather(
                *[ws.send(message_json) for ws in self.channels[channel]],
                return_exceptions=True
            )
            
    async def route_message(self, websocket, data):
        """Route message based on target"""
        msg_type = data.get('type')
        target = data.get('target')
        payload = data.get('payload', {})
        sender = self.agents.get(websocket, 'unknown')
        
        message = {
            'type': msg_type,
            'from': sender,
            'payload': payload,
            'timestamp': datetime.now().isoformat()
        }
        
        if target == 'broadcast':
            await self.broadcast(message)
        elif target.startswith('agent:'):
            agent_id = target.split(':')[1]
            await self.send_to_agent(agent_id, message)
        else:
            # Direct reply to sender
            await websocket.send(json.dumps({
                'type': 'error',
                'error': f'Unknown target: {target}',
                'timestamp': datetime.now().isoformat()
            }))
            
    async def handler(self, websocket, path):
        """WebSocket connection handler"""
        agent_id = None
        
        try:
            # Wait for registration message
            reg_msg = await websocket.recv()
            reg_data = json.loads(reg_msg)
            
            if reg_data.get('type') != 'register':
                await websocket.send(json.dumps({
                    'type': 'error',
                    'error': 'First message must be register'
                }))
                return
                
            agent_id = reg_data.get('agent_id')
            if not agent_id:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'error': 'agent_id required'
                }))
                return
                
            await self.register(websocket, agent_id)
            
            # Main message loop
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.route_message(websocket, data)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'error': 'Invalid JSON'
                    }))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed for {agent_id}")
        finally:
            await self.unregister(websocket)

async def main():
    hub = AgentHub()
    
    logger.info("=" * 50)
    logger.info("Agent Communication Hub Starting...")
    logger.info("WebSocket server on ws://localhost:9000")
    logger.info("=" * 50)
    
    async with websockets.serve(hub.handler, 'localhost', 9000):
        await asyncio.Future()  # Run forever

if __name__ == '__main__':
    asyncio.run(main())
