#!/usr/bin/env python3
"""
FORGER v4 — ACP-Based Autonomous Website Builder
Uses Agent Communication Protocol for real-time messaging
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

# Add parent to path for acp_lib
sys.path.insert(0, str(Path(__file__).parent.parent))
from acp_lib import create_agent, ACPClient

# Paths
WORKSPACE = Path("/home/chad-yi/.openclaw/workspace")
BUILDS = WORKSPACE / "agents" / "forger" / "builds"
MEMORY = WORKSPACE / "agents" / "forger" / "memory"

BUILDS.mkdir(parents=True, exist_ok=True)
MEMORY.mkdir(parents=True, exist_ok=True)

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"[FORGER-v4-ACP] {timestamp} [{level}] {msg}")

def slugify(text):
    """Create URL-friendly slug"""
    import re
    return re.sub(r'[^\w]+', '-', text.lower()).strip('-')[:50]

def parse_task(content: str) -> dict:
    """Parse task from ACP message content"""
    task = {
        'company': 'Company',
        'pages': ['index'],
        'industry': 'business',
        'color_scheme': 'professional'
    }
    
    # Extract company
    import re
    match = re.search(r'\*\*Company:\*\*\s*(.+)', content)
    if match:
        task['company'] = match.group(1).strip()
    
    # Detect pages
    if 'homepage' in content.lower() or 'index' in content.lower():
        task['pages'].append('index')
    if 'about' in content.lower():
        task['pages'].append('about')
    if 'services' in content.lower():
        task['pages'].append('services')
    if 'contact' in content.lower():
        task['pages'].append('contact')
    
    # Remove duplicates
    task['pages'] = list(set(task['pages']))
    
    return task

def build_website(company: str, pages: list, task_id: str = None) -> Path:
    """Build complete website"""
    from forger_builder import generate_page  # Reuse builder module
    
    slug = slugify(company)
    build_dir = BUILDS / f"{slug}-v4"
    
    log(f"Building {company} website ({len(pages)} pages)")
    
    for page in pages:
        content = generate_page(page, company, "business", pages, "professional")
        
        if page == 'index':
            filepath = build_dir / "index.html"
        else:
            filepath = build_dir / page / "index.html"
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content, encoding='utf-8')
        log(f"  Created: {filepath}")
    
    return build_dir

def main():
    """Main ACP agent loop"""
    log("Starting Forger v4 — ACP Mode")
    
    # Connect to ACP
    acp = create_agent("forger")
    
    if not acp.connected:
        log("Failed to connect to ACP gateway", "ERROR")
        log("Falling back to file-based mode")
        # TODO: Implement fallback
        return
    
    log("Connected to ACP. Waiting for build tasks...")
    
    # Main loop
    while True:
        try:
            # Check for messages
            messages = acp.receive_messages()
            
            for msg in messages:
                content = msg.get('content', '')
                msg_from = msg.get('from', 'unknown')
                
                log(f"Received task from {msg_from}")
                
                # Parse and build
                if 'website' in content.lower() or 'build' in content.lower():
                    task = parse_task(content)
                    
                    # Build
                    build_dir = build_website(
                        task['company'],
                        task['pages'],
                        msg.get('id')
                    )
                    
                    # Send completion back
                    acp.send_message(
                        to_agent=msg_from,
                        content=f"""# ✅ Website Build Complete

**Company:** {task['company']}
**Location:** `{build_dir}`
**Pages:** {', '.join(task['pages'])}

Build successful via ACP.
""",
                        priority="normal"
                    )
                    
                    log(f"Build complete: {task['company']}")
            
            # Sleep before next poll
            time.sleep(10)
            
        except KeyboardInterrupt:
            log("Shutting down...")
            break
        except Exception as e:
            log(f"Error: {e}", "ERROR")
            time.sleep(30)

if __name__ == "__main__":
    main()
