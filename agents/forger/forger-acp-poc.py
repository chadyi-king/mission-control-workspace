#!/usr/bin/env python3
"""
FORGER ACP Agent - Proof of Concept
Receives build tasks via ACP instead of files.
"""

import json
import asyncio
import websockets
from pathlib import Path

WORKSPACE = Path("/home/chad-yi/.openclaw/workspace")
BUILDS = WORKSPACE / "agents" / "forger" / "builds"

async def forger_acp_agent():
    """Connect to ACP and receive build tasks."""
    
    # Connect to Gateway ACP
    uri = "ws://localhost:18789/acp"
    
    print("[FORGER-ACP] Starting...")
    
    try:
        async with websockets.connect(uri) as ws:
            # Register as forger agent
            await ws.send(json.dumps({
                "type": "register",
                "agent": "forger",
                "capabilities": ["website_build"]
            }))
            
            print("[FORGER-ACP] Connected to ACP bus")
            
            while True:
                # Wait for messages
                message = await ws.recv()
                data = json.loads(message)
                
                print(f"[FORGER-ACP] Received: {data}")
                
                if data.get("type") == "build_task":
                    # Extract task details
                    company = data.get("company", "company")
                    pages = data.get("pages", ["index"])
                    
                    print(f"[FORGER-ACP] Building {company} website...")
                    
                    # Build website (simplified)
                    result = await build_website_acp(company, pages)
                    
                    # Send completion back via ACP
                    await ws.send(json.dumps({
                        "type": "build_complete",
                        "to": data.get("from", "chad-yi"),
                        "company": company,
                        "status": "success",
                        "location": str(result)
                    }))
                    
                    print(f"[FORGER-ACP] Build complete: {company}")
                    
    except Exception as e:
        print(f"[FORGER-ACP] Error: {e}")

async def build_website_acp(company, pages):
    """Build website from ACP task."""
    slug = company.lower().replace(" ", "-")
    build_dir = BUILDS / f"{slug}-acp"
    
    # Create simple HTML for each page
    for page in pages:
        if page == "index":
            filepath = build_dir / "index.html"
        else:
            filepath = build_dir / page / "index.html"
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        content = f"""<!DOCTYPE html>
<html>
<head><title>{company} - {page.title()}</title></head>
<body>
<h1>{company}</h1>
<p>Page: {page}</p>
<p>Built via ACP</p>
</body>
</html>"""
        
        filepath.write_text(content)
    
    return build_dir

if __name__ == "__main__":
    asyncio.run(forger_acp_agent())
