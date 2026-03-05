# ADVANCED OPENCLAW IMPLEMENTATION GUIDE
## Dashboards, Mission Control, Models, and Memory Optimization

**Focus Areas:** Dashboards | Mission Control | Use Cases | Implementation | Best Models | Memory Optimization

---

# SECTION 1: DASHBOARDS AND MISSION CONTROL SYSTEMS

## 1.1 The "Walking Dashboard" Concept

A "walking dashboard" is a mission control system that follows you everywhere, updates intelligently, and provides actionable information wherever you are.

**Core Principles:**

1. **Multi-Device Accessibility**
   - Web dashboard for desktop/laptop
   - Mobile-responsive for phones
   - Telegram bot for quick checks
   - Optional: Smartwatch notifications

2. **Intelligent Updates**
   - Critical alerts: Immediate
   - Status changes: 15 minutes
   - Routine updates: 2-4 hours
   - Daily digest: Morning

3. **Context Awareness**
   - Time-based (work hours vs evening)
   - Location-based (if relevant)
   - Current task awareness
   - Priority-based filtering

**Your Current Implementation:**

```
Dashboard Architecture:
├── ACTIVE.md (Human-edited source)
├── data.json (Machine-readable)
├── Helios (Sync every 15 min via cron)
├── GitHub (Version control)
├── Render (Auto-deploy hosting)
└── Telegram (Alerts and queries)
```

This is CORRECT. Don't overcomplicate it.

## 1.2 Dashboard Components Deep Dive

**Widget 1: Stats Counter**

```javascript
// data.json structure
{
  "stats": {
    "total": 85,
    "pending": 7,
    "active": 6,
    "blocked": 3,
    "review": 2,
    "done": 54
  }
}

// HTML rendering
function renderStats() {
  const stats = data.stats;
  return `
    <div class="stats-grid">
      <div class="stat-card pending">
        <div class="value">${stats.pending}</div>
        <div class="label">Pending</div>
      </div>
      <div class="stat-card active">
        <div class="value">${stats.active}</div>
        <div class="label">Active</div>
      </div>
      <div class="stat-card blocked">
        <div class="value">${stats.blocked}</div>
        <div class="label">Blocked</div>
      </div>
    </div>
  `;
}
```

**Widget 2: Urgent Queue**

```javascript
function renderUrgentQueue() {
  const urgent = data.tasks.filter(t => 
    t.priority === 'critical' || 
    (t.deadline && isOverdue(t.deadline))
  );
  
  return `
    <div class="urgent-queue">
      <h3>🔴 Urgent Items</h3>
      <ul>
        ${urgent.map(task => `
          <li class="${isOverdue(task.deadline) ? 'overdue' : 'urgent'}">
            <span class="task-id">${task.id}</span>
            <span class="task-title">${task.title}</span>
            <span class="badge">${getUrgencyLabel(task)}</span>
          </li>
        `).join('')}
      </ul>
    </div>
  `;
}
```

**Widget 3: Agent Status Grid**

```javascript
function renderAgentStatus() {
  const agents = data.agents;
  
  return `
    <div class="agent-grid">
      ${Object.entries(agents).map(([name, status]) => `
        <div class="agent-card ${status.status}">
          <div class="status-indicator ${status.status}"></div>
          <h4>${name}</h4>
          <p>${status.currentTask || 'Idle'}</p>
          <small>Last seen: ${timeAgo(status.lastHeartbeat)}</small>
        </div>
      `).join('')}
    </div>
  `;
}
```

## 1.3 Real-Time vs Polling: The Critical Decision

**Polling (Your Current Approach - CORRECT):**

```bash
# Cron job - every 15 minutes
*/15 * * * * /usr/bin/python3 /path/to/helios.py
```

**Pros:**
- Simple and reliable
- Easy to debug
- No connection management
- Works offline
- Predictable load

**Cons:**
- 15-minute delay
- Not truly real-time

**When Polling is Sufficient:**
- Task management (15 min is fine)
- Status updates (15 min is fine)
- Project tracking (15 min is fine)
- Agent health (15 min is fine)
- Daily operations (15 min is fine)

**Real-Time WebSocket (Advanced - Usually Unnecessary):**

```javascript
// Only use if you truly need sub-second updates
const ws = new WebSocket('ws://localhost:8765');

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  updateDashboard(update);
};
```

**When Real-Time is Actually Needed:**
- High-frequency trading (but OpenClaw isn't for this)
- Critical system monitoring (medical, industrial)
- Collaborative editing (Google Docs style)
- Gaming or interactive experiences

**Verdict for Personal Use:**
**POLLING IS SUFFICIENT.** The complexity of real-time systems is not worth it for personal productivity dashboards.

## 1.4 Mission Control Architecture Patterns

**Pattern 1: File-Based (Your Setup - RECOMMENDED)**

```
Human (ACTIVE.md)
    ↓
Helios (every 15 min)
    ↓
data.json
    ↓
Git push
    ↓
Render (dashboard)
    ↓
You view
```

**Pattern 2: API-Based (For Scale)**

```
Agents → REST API → Database → Dashboard API → Web UI
```

**Pattern 3: Event-Driven (Complex)**

```
Agents → Message Queue → Event Processor → Real-time Updates
```

**Recommendation:**
Stick with Pattern 1 (File-Based) until you have 50+ agents or 10,000+ tasks. It's sufficient and reliable.

---

# SECTION 2: IMPLEMENTATION STRATEGIES

## 2.1 The Perfect Agent Template

```python
#!/usr/bin/env python3
"""
Perfect Agent Template
Use this as the foundation for all agents
"""

import json
import logging
import time
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

@dataclass
class Task:
    id: str
    type: str
    data: Dict[str, Any]
    created_at: datetime
    
@dataclass  
class Result:
    task_id: str
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    completed_at: datetime = None
    
    def __post_init__(self):
        if self.completed_at is None:
            self.completed_at = datetime.now()

class PerfectAgent:
    """
    Base class for all agents
    Handles: directory setup, task processing, error handling, logging
    """
    
    def __init__(self, name: str, config: Optional[Dict] = None):
        self.name = name
        self.config = config or {}
        
        # Setup paths
        self.workspace = Path.home() / '.openclaw/workspace'
        self.agent_dir = self.workspace / 'agents' / name
        self.inbox = self.agent_dir / 'inbox'
        self.outbox = self.agent_dir / 'outbox'
        self.processed = self.inbox / 'processed'
        self.logs = self.agent_dir / 'logs'
        
        # Ensure directories exist
        self._setup_directories()
        
        # Setup logging
        self._setup_logging()
        
        # Load state
        self.state = self._load_state()
        
        self.logger.info(f"{name} agent initialized")
    
    def _setup_directories(self):
        """Create all necessary directories"""
        for dir_path in [self.inbox, self.outbox, self.processed, self.logs]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    def _setup_logging(self):
        """Configure logging"""
        log_file = self.logs / f'{datetime.now():%Y%m%d}.log'
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.name)
    
    def _load_state(self) -> Dict:
        """Load or initialize state"""
        state_file = self.agent_dir / 'state.json'
        if state_file.exists():
            return json.loads(state_file.read_text())
        return {
            'status': 'idle',
            'tasks_processed': 0,
            'errors_today': 0,
            'last_heartbeat': datetime.now().isoformat()
        }
    
    def _save_state(self):
        """Persist state to disk"""
        state_file = self.agent_dir / 'state.json'
        self.state['last_heartbeat'] = datetime.now().isoformat()
        state_file.write_text(json.dumps(self.state, indent=2))
    
    def run(self):
        """Main loop - override poll_interval in config"""
        poll_interval = self.config.get('poll_interval', 60)
        
        self.logger.info(f"Starting {self.name} main loop")
        self.state['status'] = 'active'
        
        try:
            while True:
                self._save_state()
                self.process_inbox()
                time.sleep(poll_interval)
        except KeyboardInterrupt:
            self.logger.info("Shutdown requested")
            self.state['status'] = 'stopped'
            self._save_state()
    
    def process_inbox(self):
        """Process all tasks in inbox"""
        task_files = sorted(self.inbox.glob('*.json'))
        
        for task_file in task_files:
            # Skip already processed
            if task_file.name.startswith('processed_'):
                continue
            
            try:
                # Parse task
                task = self._parse_task(task_file)
                self.logger.info(f"Processing task: {task.id}")
                
                # Execute
                result = self.execute(task)
                
                # Write result
                self._write_result(result)
                
                # Archive task
                self._archive_task(task_file)
                
                # Update stats
                self.state['tasks_processed'] += 1
                
            except Exception as e:
                self.logger.error(f"Error processing {task_file}: {e}")
                self.state['errors_today'] += 1
                self._handle_error(task_file, e)
    
    def _parse_task(self, task_file: Path) -> Task:
        """Parse task from file"""
        data = json.loads(task_file.read_text())
        return Task(
            id=data['id'],
            type=data['type'],
            data=data.get('data', {}),
            created_at=datetime.fromisoformat(data['created_at'])
        )
    
    def execute(self, task: Task) -> Result:
        """
        Override this method in subclasses
        This is where your agent logic goes
        """
        raise NotImplementedError("Subclasses must implement execute()")
    
    def _write_result(self, result: Result):
        """Write result to outbox"""
        result_file = self.outbox / f"result_{result.task_id}_{datetime.now():%Y%m%d_%H%M%S}.json"
        result_file.write_text(json.dumps(asdict(result), indent=2, default=str))
    
    def _archive_task(self, task_file: Path):
        """Move processed task to archive"""
        archive_name = f"processed_{datetime.now():%Y%m%d_%H%M%S}_{task_file.name}"
        task_file.rename(self.processed / archive_name)
    
    def _handle_error(self, task_file: Path, error: Exception):
        """Handle processing errors"""
        error_file = self.outbox / f"error_{task_file.stem}_{datetime.now():%Y%m%d_%H%M%S}.json"
        error_data = {
            'task_file': str(task_file),
            'error': str(error),
            'timestamp': datetime.now().isoformat()
        }
        error_file.write_text(json.dumps(error_data, indent=2))

# Example implementation
class MyAgent(PerfectAgent):
    """Example agent implementation"""
    
    def execute(self, task: Task) -> Result:
        # Your business logic here
        if task.type == 'EXAMPLE':
            result_data = self.process_example(task.data)
            return Result(
                task_id=task.id,
                success=True,
                data=result_data
            )
        else:
            return Result(
                task_id=task.id,
                success=False,
                error=f"Unknown task type: {task.type}"
            )
    
    def process_example(self, data: Dict) -> Dict:
        # Actual processing logic
        return {'processed': True, 'input': data}

if __name__ == '__main__':
    agent = MyAgent('my-agent', {'poll_interval': 30})
    agent.run()
```

## 2.2 Systemd Service Template

```ini
# ~/.config/systemd/user/my-agent.service
[Unit]
Description=My OpenClaw Agent
Documentation=https://github.com/chad-yi/openclaw-agents
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/chad-yi/.openclaw/workspace
ExecStart=/usr/bin/python3 agents/my-agent/agent.py
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=my-agent

# Resource limits (adjust as needed)
MemoryLimit=512M
CPUQuota=50%

[Install]
WantedBy=default.target
```

**Commands:**
```bash
# Enable and start
systemctl --user daemon-reload
systemctl --user enable my-agent
systemctl --user start my-agent

# Check status
systemctl --user status my-agent

# View logs
journalctl --user -u my-agent -f

# Stop
systemctl --user stop my-agent
```

## 2.3 Cron Scheduling Patterns

```bash
# ~/.crontab

# Helios - Dashboard sync (every 15 minutes)
*/15 * * * * cd /home/chad-yi/.openclaw/workspace && /usr/bin/python3 agents/helios/helios.py

# Daily report - 8am
0 8 * * * cd /home/chad-yi/.openclaw/workspace && /usr/bin/python3 agents/chad-yi/daily-report.py

# Health check - every hour
0 * * * * cd /home/chad-yi/.openclaw/workspace && /usr/bin/python3 agents/healthcheck/check.py

# Weekly backup - Sundays at 2am
0 2 * * 0 cd /home/chad-yi/.openclaw/workspace && ./scripts/backup.sh

# Monthly cleanup - 1st of month at 3am
0 3 1 * * cd /home/chad-yi/.openclaw/workspace && ./scripts/cleanup-old-logs.sh
```

---

# SECTION 3: BEST MODELS (FREE AND PAID)

## 3.1 Model Comparison for OpenClaw

**For CHAD_YI (The Face):**

| Model | Provider | Context | Cost | Best For |
|-------|----------|---------|------|----------|
| Kimi K2.5 | Moonshot | 2M tokens | Free tier | General coordination |
| Claude 3.5 Sonnet | Anthropic | 200K | $3/million | Complex reasoning |
| GPT-4o | OpenAI | 128K | $5/million | General purpose |
| Llama 3.1 405B | Meta | 128K | Free (self-host) | Privacy-conscious |
| Qwen 2.5 72B | Alibaba | 128K | Free tier | Multilingual |

**Recommendation for CHAD_YI:**
**Kimi K2.5 (Free tier)** - Massive 2M context window, good reasoning, free tier available through kimi.com

**For The Brain (Complex Tasks):**

| Model | Provider | Context | Cost | Best For |
|-------|----------|---------|------|----------|
| Claude 3.5 Opus | Anthropic | 200K | $15/million | Deep reasoning |
| GPT-4o | OpenAI | 128K | $5/million | Architecture design |
| DeepSeek Coder | DeepSeek | 64K | Free | Code generation |
| Codex | OpenAI | Context varies | Included | Coding tasks |

**Recommendation for Brain:**
**Claude 3.5 Opus** - Best reasoning, handles complex architecture well

**For Workforce Agents:**

| Model | Provider | Context | Cost | Best For |
|-------|----------|---------|------|----------|
| Llama 3.1 8B | Meta | 128K | Free (local) | Lightweight tasks |
| Qwen 2.5 7B | Alibaba | 128K | Free (local) | Fast responses |
| GPT-3.5 Turbo | OpenAI | 16K | $0.50/million | API integration |
| Mistral 7B | Mistral | 32K | Free (local) | Balanced |

**Recommendation for Workforce:**
**Local Llama 3.1 8B** - Fast, free, privacy-preserving

## 3.2 Free Model Setup

**Option 1: Ollama (Local Models)**

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull models
ollama pull llama3.1:8b
ollama pull qwen2.5:7b
ollama pull mistral:7b

# Run API server
ollama serve

# Test
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b",
  "prompt": "Hello, how are you?"
}'
```

**Option 2: Kimi (Free Cloud)**

```python
# Using Kimi API (free tier available)
import openai

client = openai.OpenAI(
    api_key="your-kimi-api-key",
    base_url="https://api.moonshot.cn/v1"
)

response = client.chat.completions.create(
    model="kimi-latest",
    messages=[{"role": "user", "content": "Hello"}]
)
```

**Option 3: Groq (Fast Free Tier)**

```python
from groq import Groq

client = Groq(api_key="your-groq-key")

response = client.chat.completions.create(
    model="llama-3.1-70b-versatile",
    messages=[{"role": "user", "content": "Hello"}]
)
```

## 3.3 Model Selection Strategy

**Tier 1: Local Models (Free, Private)**
- Use for: Workforce agents, simple tasks, high-volume processing
- Models: Llama 3.1 8B, Qwen 2.5 7B
- Pros: Free, fast, private, no API limits
- Cons: Lower capability than cloud models

**Tier 2: Free Cloud Tiers**  
- Use for: CHAD_YI, moderate complexity
- Services: Kimi (free tier), Groq (free tier)
- Pros: Better models, no local hardware needed
- Cons: Rate limits, requires internet

**Tier 3: Paid APIs**
- Use for: The Brain, complex reasoning, when accuracy matters
- Services: Claude, GPT-4
- Pros: Best capability, reliable
- Cons: Costs money

**Cost Optimization Strategy:**
1. Use local models for 80% of tasks (workforce)
2. Use free cloud for 15% (CHAD_YI interface)
3. Use paid APIs for 5% (complex architecture)

---

# SECTION 4: MEMORY OPTIMIZATION (Limited Context Window)

## 4.1 The Context Window Problem

**Reality:** Most models have limited context windows:
- Kimi K2.5: 2M tokens (exception)
- Claude: 200K tokens
- GPT-4: 128K tokens
- Local models: 4K-128K tokens

**Challenge:** How do we maintain continuity across sessions when the model can't hold everything in memory?

## 4.2 The Four-Tier Memory Solution

**Tier 1: SOUL.md (Core Identity)**
- Size: ~500-1000 words
- Updated: Rarely
- Purpose: Who you are, beliefs, boundaries

**Tier 2: MEMORY.md (Long-term Context)**
- Size: ~2000-5000 words
- Updated: Monthly
- Purpose: Key decisions, projects, relationships

**Tier 3: Daily Notes (Recent Events)**
- Size: Variable (~500 words/day)
- Updated: Daily
- Purpose: What happened today

**Tier 4: TOOLS.md (Technical Details)**
- Size: Variable
- Updated: As needed
- Purpose: How things work, preferences

**Total: ~10,000 words** - Fits in 200K context easily

## 4.3 Smart Loading Strategy

```python
def load_context_efficiently():
    """
    Load only what's needed to stay within context limits
    """
    context_parts = []
    
    # Always load (core identity)
    context_parts.append(read('SOUL.md'))
    context_parts.append(read('IDENTITY.md'))
    
    # Always load (who we're talking to)
    context_parts.append(read('USER.md'))
    
    # Load recent (last 2 days)
    context_parts.append(read(f'memory/{today}.md'))
    context_parts.append(read(f'memory/{yesterday}.md'))
    
    # Load relevant from long-term (search, don't load all)
    relevant = search_memory(query, top_k=5)
    for r in relevant:
        context_parts.append(read_section(r.path, r.lines))
    
    return '\n\n'.join(context_parts)
```

## 4.4 Memory Search Implementation

```python
import sqlite3
from sentence_transformers import SentenceTransformer
import numpy as np

class MemorySearch:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.db = sqlite3.connect('memory.db')
        self.init_db()
    
    def init_db(self):
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY,
                content TEXT,
                embedding BLOB,
                source TEXT,
                timestamp DATETIME
            )
        ''')
        self.db.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                content, source
            )
        ''')
    
    def add_memory(self, content, source):
        # Create embedding
        embedding = self.model.encode(content)
        
        # Store
        self.db.execute('''
            INSERT INTO memories (content, embedding, source, timestamp)
            VALUES (?, ?, ?, datetime('now'))
        ''', (content, embedding.tobytes(), source))
        
        self.db.commit()
    
    def search(self, query, top_k=5):
        # Create query embedding
        query_emb = self.model.encode(query)
        
        # Search all memories
        results = []
        for row in self.db.execute('SELECT content, embedding, source FROM memories'):
            content, emb_bytes, source = row
            emb = np.frombuffer(emb_bytes, dtype=np.float32)
            similarity = np.dot(query_emb, emb) / (np.linalg.norm(query_emb) * np.linalg.norm(emb))
            results.append((similarity, content, source))
        
        # Return top k
        results.sort(reverse=True)
        return results[:top_k]
```

## 4.5 Context Pruning Strategy

When context gets too long:

```python
def prune_context(context, max_tokens=100000):
    """
    Intelligently reduce context size while preserving meaning
    """
    # Strategy 1: Summarize old daily notes
    if len(context) > max_tokens:
        old_notes = extract_old_notes(context)
        summary = summarize(old_notes)
        context = replace_with_summary(context, old_notes, summary)
    
    # Strategy 2: Remove redundant information
    if len(context) > max_tokens:
        context = remove_duplicates(context)
    
    # Strategy 3: Keep only most relevant search results
    if len(context) > max_tokens:
        context = keep_top_search_results(context, n=3)
    
    return context
```

## 4.6 The "Crazy Network" Pattern

**Concept:** Multiple specialized agents, each with focused memory

```
CHAD_YI (The Face)
├── Short-term memory (current conversation)
├── Routes to specialized agents
│
├── Trading Agent (Quanta)
│   ├── Trading history DB
│   ├── Market analysis memory
│   └── Risk management rules
│
├── Builder Agent (Forger)
│   ├── Project templates
│   ├── Code patterns
│   └── Client preferences
│
├── Auditor Agent (Helios)
│   ├── Task history
│   ├── Dashboard state
│   └── Sync schedules
│
└── Research Agent
    ├── Research notes
    ├── Source database
    └── Analysis methods
```

**Benefits:**
- Each agent only loads relevant memory
- Specialized agents can use smaller models
- Parallel processing possible
- Easier to debug and maintain

---

# SECTION 5: USE CASES AND IMPLEMENTATIONS

## 5.1 Trading Agent (Quanta Pattern)

```python
class TradingAgent(PerfectAgent):
    """
    Suggestion-only trading agent
    NEVER executes without approval
    """
    
    def __init__(self):
        super().__init__('quanta', {'poll_interval': 30})
        self.db = sqlite3.connect('trades.db')
        self.setup_database()
    
    def setup_database(self):
        self.db.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                symbol TEXT,
                direction TEXT,
                entry REAL,
                stop_loss REAL,
                size INTEGER,
                status TEXT,
                opened_at TIMESTAMP,
                oanda_id TEXT
            )
        ''')
    
    def execute(self, task: Task) -> Result:
        if task.type == 'ANALYZE_SIGNAL':
            return self.analyze_signal(task.data)
        elif task.type == 'PROCESS_APPROVAL':
            return self.process_approval(task.data)
        else:
            return Result(task.id, False, error=f"Unknown: {task.type}")
    
    def analyze_signal(self, signal):
        """Analyze signal and create proposal"""
        # Calculate position size
        account = self.get_account_balance()
        risk = account * 0.02  # 2%
        
        position_size = self.calculate_position_size(
            risk_amount=risk,
            stop_pips=signal['stop_pips'],
            pip_value=self.get_pip_value(signal['symbol'])
        )
        
        # Create proposal
        proposal = {
            'type': 'TRADE_PROPOSAL',
            'signal': signal,
            'position_size': position_size,
            'risk_amount': risk,
            'account_balance': account
        }
        
        # Write to CHAD_YI inbox (NOT execute)
        self.write_to_chad_yi_inbox(proposal)
        
        return Result(
            task_id='analyze',
            success=True,
            data={'proposal_created': True}
        )
    
    def write_to_chad_yi_inbox(self, proposal):
        """Send proposal for human approval"""
        inbox = Path('agents/chad-yi/inbox')
        file = inbox / f"TRADE_PROPOSAL_{datetime.now():%Y%m%d_%H%M%S}.json"
        file.write_text(json.dumps(proposal, indent=2))
```

## 5.2 Website Builder (Forger Pattern)

```python
class WebsiteBuilderAgent(PerfectAgent):
    """
    Website development agent
    """
    
    def __init__(self):
        super().__init__('forger', {'poll_interval': 60})
        self.builds_dir = Path('builds')
        self.builds_dir.mkdir(exist_ok=True)
    
    def execute(self, task: Task) -> Result:
        if task.type == 'BUILD_WEBSITE':
            return self.build_website(task.data)
        elif task.type == 'UPDATE_WEBSITE':
            return self.update_website(task.data)
        else:
            return Result(task.id, False, error=f"Unknown: {task.type}")
    
    def build_website(self, spec):
        """Build website from specification"""
        build_id = f"{spec['name']}_{datetime.now():%Y%m%d_%H%M%S}"
        build_dir = self.builds_dir / build_id
        build_dir.mkdir()
        
        # Generate pages
        for page in spec['pages']:
            html = self.generate_page(page, spec)
            (build_dir / f"{page['name']}.html").write_text(html)
        
        # Generate CSS
        css = self.generate_styles(spec)
        (build_dir / "styles.css").write_text(css)
        
        # Create manifest
        manifest = {
            'build_id': build_id,
            'spec': spec,
            'pages': [p['name'] for p in spec['pages']],
            'created_at': datetime.now().isoformat()
        }
        (build_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
        
        return Result(
            task_id='build',
            success=True,
            data={'build_id': build_id, 'path': str(build_dir)}
        )
```

## 5.3 Research Agent Pattern

```python
class ResearchAgent(PerfectAgent):
    """
    Research and analysis agent
    """
    
    def execute(self, task: Task) -> Result:
        if task.type == 'RESEARCH_TOPIC':
            return self.research_topic(task.data)
        elif task.type == 'ANALYZE_DATA':
            return self.analyze_data(task.data)
        else:
            return Result(task.id, False, error=f"Unknown: {task.type}")
    
    def research_topic(self, params):
        """Research a topic and compile findings"""
        topic = params['topic']
        depth = params.get('depth', 'standard')
        
        # Search sources
        findings = []
        
        # Web search (if configured)
        if self.config.get('enable_web_search'):
            web_results = self.search_web(topic)
            findings.extend(web_results)
        
        # Local knowledge base
        local_results = self.search_local_kb(topic)
        findings.extend(local_results)
        
        # Compile report
        report = self.compile_report(findings, depth)
        
        return Result(
            task_id='research',
            success=True,
            data={'report': report, 'sources': len(findings)}
        )
```

---

# SECTION 6: DEPLOYMENT AND OPERATIONS

## 6.1 Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent code
COPY agents/ ./agents/

# Setup directories
RUN mkdir -p /app/data /app/logs

# Non-root user
RUN useradd -m -u 1000 agent
USER agent

# Run agent
CMD ["python", "agents/my-agent/agent.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  helios:
    build: .
    container_name: helios
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - AGENT_NAME=helios
      - POLL_INTERVAL=900
    restart: unless-stopped
  
  forger:
    build: .
    container_name: forger
    volumes:
      - ./data:/app/data
      - ./builds:/app/builds
    environment:
      - AGENT_NAME=forger
    restart: unless-stopped
```

## 6.2 Cloud Deployment (AWS Example)

```yaml
# serverless.yml
service: openclaw-agents

provider:
  name: aws
  runtime: python3.11
  region: ap-southeast-1

functions:
  helios:
    handler: agents/helios/lambda.handler
    events:
      - schedule: rate(15 minutes)
    environment:
      DASHBOARD_REPO: ${env:DASHBOARD_REPO}
  
  webhook:
    handler: agents/chad-yi/webhook.handler
    events:
      - http:
          path: /webhook
          method: post
```

## 6.3 Monitoring Stack

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-storage:/var/lib/grafana
  
  loki:
    image: grafana/loki
    ports:
      - "3100:3100"

volumes:
  grafana-storage:
```

---

# CONCLUSION

## Key Implementation Takeaways

1. **Start Simple** - File-based architecture is sufficient for 99% of use cases
2. **Use Free Models** - Kimi, Ollama, Groq provide excellent capabilities for free
3. **Optimize Memory** - Four-tier memory system keeps context manageable
4. **Perfect the Template** - Use the PerfectAgent base class for all agents
5. **Monitor Everything** - Health checks, logs, and dashboards from day one

## Recommended Stack

**Models:**
- CHAD_YI: Kimi K2.5 (free tier)
- Brain: Claude 3.5 (when needed)
- Workforce: Local Llama 3.1 8B

**Infrastructure:**
- File-based communication
- SQLite for data
- Cron for scheduling
- Systemd for services
- Render for dashboard

**Development:**
- Python 3.11+
- VS Code with extensions
- Git for version control
- Docker for deployment

---

**Document Location:** `/home/chad-yi/.openclaw/workspace/ADVANCED_IMPLEMENTATION_GUIDE.md`  
**Focus:** Dashboards | Models | Memory | Implementation | Use Cases