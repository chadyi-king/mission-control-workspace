#!/usr/bin/env python3
"""
Forger Autonomous Agent v2.0
Web Architect with tool access
"""

import asyncio
import sys
import os

# Setup logging first
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add infrastructure to path
sys.path.insert(0, '/home/chad-yi/.openclaw/workspace/infrastructure')

# Import client
try:
    from agent_client import AgentClient
except ImportError as e:
    logger.error(f"Failed to import AgentClient: {e}")
    # Fallback - define minimal version
    class AgentClient:
        def __init__(self, agent_id):
            self.agent_id = agent_id
        def exec(self, cmd, timeout=30):
            import subprocess
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            return {'stdout': result.stdout, 'stderr': result.stderr, 'returncode': result.returncode}
        def file_write(self, path, content):
            full_path = os.path.join('/home/chad-yi/.openclaw/workspace', path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
            return {'success': True}
        def file_read(self, path):
            full_path = os.path.join('/home/chad-yi/.openclaw/workspace', path)
            try:
                with open(full_path, 'r') as f:
                    return {'content': f.read()}
            except Exception as e:
                return {'error': str(e)}
        async def connect(self):
            pass
        def health_check(self):
            return {'status': 'fallback_mode'}
        def image_gen(self, prompt, size='1024x1024'):
            logger.info(f"[FALLBACK] Image generation requested: {prompt[:50]}...")
            return {'error': 'OpenAI API key not configured', 'status': 'fallback', 'note': 'Add API key to tool-bridge/api-keys.json'}

import json
from datetime import datetime

class ForgerAgent:
    def __init__(self):
        self.client = AgentClient('forger')
        self.base_dir = '/home/chad-yi/.openclaw/workspace/agents/forger'
        self.inbox_dir = os.path.join(self.base_dir, 'inbox')
        self.outbox_dir = os.path.join(self.base_dir, 'outbox')
        self.projects_dir = os.path.join(self.base_dir, 'projects')
        
    async def run(self):
        """Main agent loop"""
        logger.info("=" * 50)
        logger.info("FORGER v2.0 - Web Architect Starting")
        logger.info("=" * 50)
        
        # Connect to infrastructure
        await self.client.connect()
        
        # Check tool bridge health
        health = self.client.health_check()
        logger.info(f"Tool bridge health: {health}")
        
        # Process tasks
        await self.process_tasks()
        
    async def process_tasks(self):
        """Check inbox and process tasks"""
        import glob
        
        if not os.path.exists(self.inbox_dir):
            logger.info("No inbox directory")
            return
            
        task_files = glob.glob(os.path.join(self.inbox_dir, 'TASK-*.md'))
        
        if not task_files:
            logger.info("No tasks in inbox")
            return
            
        logger.info(f"Found {len(task_files)} task(s)")
        
        for task_file in sorted(task_files, key=os.path.getmtime):
            task_name = os.path.basename(task_file)
            logger.info(f"Processing: {task_name}")
            
            # Read task
            result = self.client.file_read(f'agents/forger/inbox/{task_name}')
            if 'error' in result:
                logger.error(f"Failed to read task: {result['error']}")
                continue
                
            task_content = result.get('content', '')
            
            # Process based on task type
            if 'HERO-VISUAL' in task_name.upper():
                await self.create_hero_visual(task_content)
            elif 'WEBSITE' in task_name.upper():
                await self.create_website(task_content)
            else:
                await self.generic_response(task_name, task_content)
                
    async def create_hero_visual(self, task_content):
        """Create hero banner visual for Elluminate"""
        logger.info("Creating hero visual for B6-Elluminate...")
        
        # Generate image using tool bridge
        prompt = """Professional hero banner for team building company "Elluminate".
Three stylized figures side by side:
- Left: Business professional woman in blue with blue glowing lightbulb above head
- Center: Youth/student in orange/red with orange glowing lightbulb above head  
- Right: Trainer/coach in green with green glowing lightbulb above head
Headline: "Ignite the SPARK within your TEAM"
Modern, energetic, professional design. Clean background with subtle team activity photos.
Flat illustration style, not photorealistic."""

        result = self.client.image_gen(prompt, '1792x1024')
        
        if 'error' in result:
            logger.error(f"Image generation failed: {result['error']}")
            # Write spec instead
            await self.write_hero_spec()
        else:
            logger.info(f"Image generation: {result}")
            # Note: Actual image would be downloaded from OpenAI response
            await self.write_hero_spec()
            
    async def write_hero_spec(self):
        """Write detailed hero banner specification"""
        from datetime import datetime
        timestamp = datetime.now().isoformat()
        spec = f"""# B6-Elluminate Hero Banner - Technical Spec
**Generated by Forger** - {timestamp}

## Design Specifications

### Layout
```
┌─────────────────────────────────────────────────────────┐
│  [Photo collage background - desaturated 30%]            │
│                                                         │
│         IGNITE THE SPARK                                │
│         WITHIN YOUR TEAM                                │
│                                                         │
│  [Figure 1]    [Figure 2]    [Figure 3]                │
│    💡 BLUE      💡 ORANGE      💡 GREEN                │
│                                                         │
│ Corporate • School • Trainings • Retreats              │
│                                                         │
│         [ Get Started → ]                               │
└─────────────────────────────────────────────────────────┘
```

### Colors
- Primary: Forest Green #2E5C4F
- Accent: Warm Orange #F4A261
- Figure 1 glow: Corporate Blue #4A90D9
- Figure 2 glow: Warm Orange #F4A261
- Figure 3 glow: Forest Green #2E5C4F
- Background: Cream #FDF8F3 at 90% opacity

### Typography
- Headline: Inter ExtraBold 4rem (desktop), 2.5rem (mobile)
- "SPARK" in orange accent color
- Service labels: Inter SemiBold, small caps
- CTA: Inter Bold, Forest Green background

### Implementation Notes
1. Use CSS Grid for layout
2. SVG for lightbulb glow effects
3. Background: CSS multiple backgrounds with blend modes
4. Responsive: Stack to single column on mobile
5. Animation: Subtle pulse on lightbulbs (optional)

## Assets Needed
- [ ] 3 character illustrations (or silhouettes)
- [ ] Background photo collage (4-6 desaturated images)
- [ ] Lightbulb SVG with glow filter
"""

        result = self.client.file_write(
            'agents/forger/projects/B6-elluminate/designs/HERO-BANNER-SPEC.md',
            spec
        )
        
        if result.get('success'):
            logger.info("✅ Hero banner spec written")
        else:
            logger.error(f"Failed to write spec: {result}")
            
    async def create_website(self, task_content):
        """Create website HTML/CSS"""
        logger.info("Creating website...")
        
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Elluminate - Team Building Singapore</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --forest-green: #2E5C4F;
            --warm-orange: #F4A261;
            --cream: #FDF8F3;
            --charcoal: #2D2D2D;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: var(--cream);
            color: var(--charcoal);
        }
        
        .hero {
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, var(--cream) 0%, #fff 100%);
        }
        
        .hero h1 {
            font-size: 4rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 1rem;
        }
        
        .hero h1 span {
            color: var(--warm-orange);
        }
        
        .services {
            display: flex;
            gap: 2rem;
            margin: 2rem 0;
            flex-wrap: wrap;
            justify-content: center;
        }
        
        .cta-button {
            background: var(--forest-green);
            color: white;
            padding: 1rem 2rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 700;
            font-size: 1.1rem;
            transition: transform 0.2s;
        }
        
        .cta-button:hover {
            transform: translateY(-2px);
        }
        
        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2.5rem;
            }
        }
    </style>
</head>
<body>
    <section class="hero">
        <h1>Ignite the <span>SPARK</span><br>within your TEAM</h1>
        
        <div class="services">
            <span>Corporate Teambuilding</span>
            <span>•</span>
            <span>School Programs</span>
            <span>•</span>
            <span>Trainings</span>
            <span>•</span>
            <span>Retreats</span>
        </div>
        
        <a href="#contact" class="cta-button">Get Started →</a>
    </section>
</body>
</html>"""

        result = self.client.file_write(
            'agents/forger/projects/B6-elluminate/dist/index.html',
            html
        )
        
        if result.get('success'):
            logger.info("✅ Website HTML written to dist/index.html")
        else:
            logger.error(f"Failed to write website: {result}")
            
    async def generic_response(self, task_name, task_content):
        """Generic response for unknown tasks"""
        response = f"""# Forger Response: {task_name}
**Received:** {datetime.now().isoformat()}
**Status:** Task received, needs clarification

I've received your task but need more specific instructions on what to build.

**My capabilities:**
- Generate hero banners and visuals
- Build website HTML/CSS
- Create design specifications

**Please specify:**
1. What exactly should I create?
2. What format? (HTML, image spec, design doc)
3. Any specific requirements?

**Tool bridge status:** {self.client.health_check()}
"""
        
        import glob
        timestamp = datetime.now().strftime('%Y%m%d-%H%M')
        response_file = f'{self.outbox_dir}/response-{timestamp}-{task_name}'
        
        result = self.client.file_write(
            f'agents/forger/outbox/response-{timestamp}-{task_name}',
            response
        )
        
        if result.get('success'):
            logger.info(f"✅ Response written")
        else:
            logger.error(f"Failed to write response: {result}")

if __name__ == '__main__':
    agent = ForgerAgent()
    asyncio.run(agent.run())
