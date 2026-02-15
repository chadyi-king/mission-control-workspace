#!/usr/bin/env python3
"""
Tool Bridge Service
Provides agents with tool capabilities via REST API
"""

from flask import Flask, request, jsonify
import subprocess
import os
import json
import logging
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API key storage (load from file)
API_KEYS_FILE = os.path.join(os.path.dirname(__file__), 'api-keys.json')

def load_api_keys():
    """Load API keys from file"""
    if os.path.exists(API_KEYS_FILE):
        with open(API_KEYS_FILE) as f:
            return json.load(f)
    return {
        'openai': None,
        'allowed_agents': ['forger', 'helios', 'escritor', 'quanta', 'mensamusa', 'autour', 'chad_yi']
    }

api_keys = load_api_keys()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'tools_available': ['exec', 'file_write', 'file_read', 'image_gen']
    })

@app.route('/exec', methods=['POST'])
def exec_command():
    """Execute shell command"""
    data = request.json
    agent_id = data.get('agent_id')
    command = data.get('command')
    timeout = data.get('timeout', 30)
    
    if not agent_id or agent_id not in api_keys.get('allowed_agents', []):
        return jsonify({'error': 'Unauthorized agent'}), 403
    
    if not command:
        return jsonify({'error': 'No command provided'}), 400
    
    # Security: block dangerous commands
    blocked = ['rm -rf /', '> /dev/', ':(){ :|:& };:', 'mkfs']
    for b in blocked:
        if b in command:
            return jsonify({'error': f'Blocked command contains: {b}'}), 403
    
    try:
        logger.info(f"[{agent_id}] Executing: {command[:50]}...")
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        return jsonify({
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode,
            'timestamp': datetime.now().isoformat()
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Command timed out'}), 408
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/file/write', methods=['POST'])
def file_write():
    """Write file to workspace"""
    data = request.json
    agent_id = data.get('agent_id')
    path = data.get('path')
    content = data.get('content')
    
    if not agent_id or agent_id not in api_keys.get('allowed_agents', []):
        return jsonify({'error': 'Unauthorized agent'}), 403
    
    if not path or content is None:
        return jsonify({'error': 'Path and content required'}), 400
    
    # Security: only allow writes within workspace
    base_dir = os.path.expanduser('~/.openclaw/workspace')
    full_path = os.path.join(base_dir, path)
    
    if not full_path.startswith(base_dir):
        return jsonify({'error': 'Path outside workspace'}), 403
    
    try:
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
        
        logger.info(f"[{agent_id}] Wrote: {path}")
        return jsonify({
            'success': True,
            'path': path,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/file/read', methods=['POST'])
def file_read():
    """Read file from workspace"""
    data = request.json
    agent_id = data.get('agent_id')
    path = data.get('path')
    
    if not agent_id or agent_id not in api_keys.get('allowed_agents', []):
        return jsonify({'error': 'Unauthorized agent'}), 403
    
    if not path:
        return jsonify({'error': 'Path required'}), 400
    
    base_dir = os.path.expanduser('~/.openclaw/workspace')
    full_path = os.path.join(base_dir, path)
    
    if not full_path.startswith(base_dir):
        return jsonify({'error': 'Path outside workspace'}), 403
    
    try:
        with open(full_path, 'r') as f:
            content = f.read()
        
        return jsonify({
            'content': content,
            'path': path,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/image/gen', methods=['POST'])
def image_gen():
    """Generate image using OpenAI"""
    data = request.json
    agent_id = data.get('agent_id')
    prompt = data.get('prompt')
    size = data.get('size', '1024x1024')
    
    if not agent_id or agent_id not in api_keys.get('allowed_agents', []):
        return jsonify({'error': 'Unauthorized agent'}), 403
    
    if not prompt:
        return jsonify({'error': 'Prompt required'}), 400
    
    openai_key = api_keys.get('openai')
    if not openai_key:
        return jsonify({'error': 'OpenAI API key not configured'}), 503
    
    # This would call OpenAI API
    # For now, return mock response
    logger.info(f"[{agent_id}] Image gen requested: {prompt[:50]}...")
    
    return jsonify({
        'status': 'queued',
        'prompt': prompt,
        'size': size,
        'timestamp': datetime.now().isoformat(),
        'note': 'OpenAI integration pending - add API key to api-keys.json'
    })

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("Tool Bridge Service Starting...")
    logger.info("REST API on http://localhost:9001")
    logger.info("=" * 50)
    app.run(host='localhost', port=9001, debug=False)
