

### 2.1 Detailed Role Analysis: The Face (CHAD_YI)

**The Face as Interface Layer:**

The Face serves as the sole point of contact between the human operator and the entire agent ecosystem. This is not just a technical convenience; it is a fundamental architectural decision that ensures consistency, safety, and comprehensibility.

**Core Responsibilities Expanded:**

**1. Communication Management:**

The Face handles all communication with the human across all channels. In your case, this is primarily Telegram, but OpenClaw supports multiple channels including web chat, voice, and messaging platforms.

**Communication Patterns:**

*Incoming (Human → System):*
- Human sends message via Telegram
- OpenClaw Gateway receives message
- Message routed to CHAD_YI
- CHAD_YI reads identity files (SOUL.md, IDENTITY.md, USER.md)
- CHAD_YI searches memory for context
- CHAD_YI formulates response

*Outgoing (System → Human):*
- Agent writes to outbox/
- CHAD_YI polls outbox directories
- CHAD_YI reads agent output
- CHAD_YI formats for human consumption
- CHAD_YI sends via appropriate channel

**Communication Best Practices:**

**Conciseness:**
The Face should be concise. Humans have limited attention spans. Long messages are less likely to be read fully.

**Formatting:**
Use formatting to improve readability:
- Headers for sections
- Bullet points for lists
- Bold for emphasis
- Emojis for visual scanning

**Context Preservation:**
The Face must maintain context across messages. This is why SOUL.md and MEMORY.md are read at the start of every session.

**Example: Good vs Bad Communication:**

*Bad (Too long, poor formatting):*
```
Hello! I have checked all the agents and found that Helios is currently running and performing its regular audits every 15 minutes. Forger is currently in an idle state waiting for new tasks to be assigned. Quanta is currently stopped due to previous issues with tracking that resulted in some financial losses. The dashboard shows that there are currently 80 total tasks in the system with 7 pending, 6 active, 3 blocked, 2 in review, and 54 completed. The urgent items that require your attention include task A1-6 which is overdue, and task B6-8 which is due tomorrow...
```

*Good (Concise, well-formatted):*
```
Agent Status - 22:00 SGT

🟢 Helios: Running (synced 2 min ago)
🟡 Forger: Idle (waiting for tasks)
🔴 Quanta: OFF (needs rebuild)

Task Overview
• Total: 80 | Pending: 7 | Active: 6 | Blocked: 3

Urgent Items
• 🔴 A1-6: Sign contract (OVERDUE)
• 🟡 B6-8: Order items (Due tomorrow)

No other issues requiring attention.
```

**2. Context and Memory Management:**

The Face is responsible for maintaining continuity across sessions. This involves several mechanisms:

**Session Start Protocol:**
```python
def start_session():
    # 1. Read identity
    soul = read('SOUL.md')
    identity = read('IDENTITY.md')
    user = read('USER.md')
    
    # 2. Read recent memory
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    read(f'memory/{today}.md')
    read(f'memory/{yesterday}.md')
    
    # 3. Check for updates
    check_agent_outboxes()
    check_dashboard_status()
    
    # Ready to respond
```

**Memory Search:**
Before answering questions about prior work, the Face searches memory:
```python
def answer_question(question):
    # Search for relevant context
    results = memory_search(question)
    
    # Read specific sections if found
    for result in results:
        memory_get(result.path, result.from, result.lines)
    
    # Formulate answer based on actual memory
    return formulate_answer(question, results)
```

**Memory Updates:**
After significant events, the Face updates memory:
```python
def log_event(event):
    # Write to daily log
    today = datetime.now().strftime('%Y-%m-%d')
    append(f'memory/{today}.md', format_event(event))
    
    # Update MEMORY.md if significant
    if event.significance == 'high':
        update_memory_md(event)
```

**3. Coordination and Routing:**

The Face decides which agent should handle each task and routes work appropriately.

**Routing Logic:**
```python
def route_task(task):
    # Determine appropriate agent
    if task.type == 'website_build':
        return 'forger'
    elif task.type == 'trading_analysis':
        return 'quanta'
    elif task.type == 'audit_sync':
        return 'helios'
    elif task.type == 'complex_architecture':
        return 'cerebronn'
    else:
        return 'chad-yi'  # Handle directly
```

**Task Delegation:**
```python
def delegate_task(agent, task):
    # Write task to agent's inbox
    task_file = format_task_file(task)
    write(f'agents/{agent}/inbox/{task.id}.md', task_file)
    
    # Notify agent (if they have notification mechanism)
    notify_agent(agent, f'New task: {task.title}')
```

**Result Aggregation:**
```python
def check_agent_results():
    results = []
    
    for agent in get_all_agents():
        outbox_files = list_files(f'agents/{agent}/outbox/')
        
        for file in outbox_files:
            result = read_file(file)
            results.append({
                'agent': agent,
                'result': result,
                'file': file
            })
            
            # Archive after reading
            archive_file(file)
    
    return results
```

**4. Approval Workflow Management:**

The Face is the gatekeeper for critical actions. This is the most important responsibility.

**Approval Workflow Implementation:**
```python
def request_approval(proposal):
    # Format proposal for human
    message = format_proposal(proposal)
    
    # Send to human
    send_to_human(message)
    
    # Wait for response
    # (In practice, this happens across sessions)
    return 'PENDING'

def process_approval_response(response, original_proposal):
    if response.approved:
        # Write approval to agent inbox
        approval = {
            'type': 'APPROVAL',
            'original_proposal': original_proposal.id,
            'timestamp': datetime.now()
        }
        write_to_inbox(original_proposal.agent, approval)
        
        return 'APPROVED'
        
    else:
        # Log rejection
        log_rejection(original_proposal, response.reason)
        
        return 'REJECTED'
```

**Critical Actions Requiring Approval:**

The Face must request approval for:
- Financial transactions (trades, transfers, purchases)
- Code deployment to production
- External communications (emails, posts, messages)
- Data deletion or modification
- System configuration changes
- Agent creation or deletion

**5. Safety and Error Prevention:**

The Face acts as a safety layer, preventing dangerous actions.

**Safety Checks:**
```python
def validate_action(action):
    # Check if action is on safety list
    if action.type in CRITICAL_ACTIONS:
        # Must have explicit approval
        if not has_approval(action.id):
            return False, 'Requires explicit approval'
    
    # Check for common mistakes
    if action.type == 'trade':
        if action.size > MAX_POSITION_SIZE:
            return False, 'Position size exceeds limit'
        
        if not action.stop_loss:
            return False, 'Stop loss is mandatory'
    
    return True, 'OK'
```

**Error Handling:**
```python
def handle_error(error):
    # Log error
    log_error(error)
    
    # Notify human if critical
    if error.severity == 'critical':
        send_alert(f'CRITICAL ERROR: {error.message}')
    
    # Attempt recovery if possible
    if error.recoverable:
        attempt_recovery(error)
    
    # Document for future reference
    update_troubleshooting_guide(error)
```

### 2.2 Communication Flow Examples (Detailed)

**Example 1: Simple Task Assignment - Complete Flow**

*Step 1: Human Request*
```
Caleb: "Build me a website for Elluminate"
```

*Step 2: CHAD_YI Processing*
```python
# Read context
read('SOUL.md')
read('IDENTITY.md')
read('USER.md')

# Search for relevant info
memory_search('Elluminate website')

# Determine appropriate agent
agent = 'forger'

# Create task
task = {
    'id': f'B6-BUILD-{timestamp}',
    'type': 'website_build',
    'company': 'Elluminate',
    'requirements': [
        'Corporate website',
        'Services pages',
        'Contact form',
        'Mobile responsive'
    ],
    'priority': 'high',
    'created_at': datetime.now()
}

# Write to agent inbox
write(f'agents/{agent}/inbox/{task.id}.md', format_task(task))

# Respond to human
send_message("Task created and assigned to Forger. I'll notify you when complete.")
```

*Step 3: Forger Processing*
```python
# Check inbox
inbox_files = list_files('inbox/')

for file in inbox_files:
    task = read_task(file)
    
    # Execute task
    website = build_website(task)
    
    # Write result to outbox
    result = {
        'type': 'BUILD_COMPLETE',
        'task_id': task.id,
        'output_path': website.path,
        'pages': website.pages,
        'timestamp': datetime.now()
    }
    write(f'outbox/{task.id}-COMPLETE.md', format_result(result))
    
    # Archive task
    archive_file(file)
```

*Step 4: CHAD_YI Reporting*
```python
# Poll outbox directories
results = check_agent_outboxes()

for result in results:
    if result.type == 'BUILD_COMPLETE':
        # Format for human
        message = format_build_notification(result)
        
        # Send to human
        send_message(message)
        
        # Archive result
        archive_file(result.file)
```

*Step 5: Human Response*
```
Caleb: "Show me the website"
```

*Step 6: CHAD_YI Serving Content*
```python
# Read built website
website = read_build_output(result.output_path)

# Format for display
preview = generate_preview(website)

# Send to human
send_message_with_attachment("Here's the website preview:", preview)
```

*Step 7: Human Approval*
```
Caleb: "Looks good, deploy it"
```

*Step 8: CHAD_YI Execution*
```python
# Deploy website
deployment = deploy_website(website)

# Report result
send_message(f"Website deployed successfully. URL: {deployment.url}")
```

**Example 2: Trading Proposal - Complete Flow with Approval**

*Step 1: Signal Detection*
```python
# Quanta monitors for signals
signal = detect_signal()

if signal:
    # Create proposal
    proposal = {
        'type': 'TRADE_PROPOSAL',
        'signal': {
            'pair': signal.pair,
            'direction': signal.direction,
            'entry': signal.entry,
            'stop_loss': signal.stop_loss,
            'take_profits': signal.take_profits
        },
        'analysis': {
            'trend': signal.trend,
            'support': signal.support,
            'resistance': signal.resistance
        },
        'risk': {
            'position_size': calculate_position_size(signal),
            'risk_amount': calculate_risk_amount(signal),
            'risk_percent': calculate_risk_percent(signal)
        },
        'timestamp': datetime.now()
    }
    
    # Write to CHAD_YI inbox
    write('agents/chad-yi/inbox/TRADE_PROPOSAL.md', format_proposal(proposal))
```

*Step 2: CHAD_YI Review*
```python
# Read proposal
proposal = read_proposal('inbox/TRADE_PROPOSAL.md')

# Format for human
message = f"""
📊 TRADE PROPOSAL

Pair: {proposal.signal.pair}
Direction: {proposal.signal.direction}
Entry: {proposal.signal.entry}
Stop Loss: {proposal.signal.stop_loss}
Take Profits: {', '.join(proposal.signal.take_profits)}

Position Size: {proposal.risk.position_size} units
Risk Amount: ${proposal.risk.risk_amount}
Risk Percent: {proposal.risk.risk_percent}%

Approve this trade? Reply YES or NO.
"""

# Send to human
send_message(message)

# Archive proposal
archive_file('inbox/TRADE_PROPOSAL.md')
```

*Step 3: Human Decision*
```
Caleb: "YES"
```

*Step 4: CHAD_YI Processing Approval*
```python
# Record approval
approval = {
    'type': 'TRADE_APPROVAL',
    'original_proposal': proposal.id,
    'timestamp': datetime.now()
}

# Write to Quanta inbox
write('agents/quanta/inbox/APPROVED.md', format_approval(approval))

# Confirm to human
send_message("Trade approved. Executing now...")
```

*Step 5: Quanta Execution*
```python
# Read approval
approval = read_approval('inbox/APPROVED.md')

# Execute trade
trade_result = execute_trade(proposal.signal)

# Record trade
record_trade(trade_result)

# Write result to outbox
result = {
    'type': 'TRADE_EXECUTED',
    'trade_id': trade_result.id,
    'status': trade_result.status,
    'timestamp': datetime.now()
}
write('outbox/TRADE_EXECUTED.md', format_result(result))

# Archive approval
archive_file('inbox/APPROVED.md')
```

*Step 6: CHAD_YI Reporting*
```python
# Read result
result = read_result('agents/quanta/outbox/TRADE_EXECUTED.md')

# Format for human
message = f"""
✅ TRADE EXECUTED

Trade ID: {result.trade_id}
Status: {result.status}
Time: {result.timestamp}
"""

# Send to human
send_message(message)
```

### 2.3 The Brain (Cerebronn-Type) in Detail

**When to Use The Brain:**

The Brain is valuable for:
- Complex architectural decisions requiring multiple considerations
- Multi-step planning with dependencies
- Research tasks requiring synthesis of multiple sources
- Code review and refactoring decisions
- Long-term strategy development

The Brain is NOT needed for:
- Simple task execution
- Routine coordination
- Information retrieval
- Quick responses

**Brain Communication Pattern:**

The Brain operates on a different timescale than the Face. While the Face responds in real-time (seconds), the Brain may take hours to complete a task.

**Example: Architecture Planning Flow**

*Step 1: Task Assignment*
```
Caleb: "Plan the architecture for the new Elluminate website"
```

*Step 2: CHAD_YI Delegation*
```python
# Create architecture task
task = {
    'id': f'ARCH-{timestamp}',
    'type': 'architecture_planning',
    'project': 'Elluminate',
    'requirements': [
        'Corporate website',
        'Service listings',
        'Contact forms',
        'Mobile responsive',
        'SEO optimized'
    ],
    'constraints': [
        'Budget: $500',
        'Timeline: 2 weeks',
        'Tech: Modern, maintainable'
    ]
}

# Write to Brain inbox
write('agents/cerebronn/inbox/ARCHITECTURE_TASK.md', format_task(task))

# Respond to human
send_message("Architecture planning task assigned to Cerebronn. This may take a few hours. I'll notify you when complete.")
```

*Step 3: Brain Processing (Hours Later)*
```python
# Read task
task = read_task('inbox/ARCHITECTURE_TASK.md')

# Deep analysis
architecture = analyze_requirements(task)
tech_stack = select_tech_stack(task, architecture)
component_design = design_components(architecture)
data_model = design_data_model(architecture)

# Create comprehensive plan
plan = {
    'type': 'ARCHITECTURE_PLAN',
    'task_id': task.id,
    'overview': architecture.overview,
    'tech_stack': tech_stack,
    'components': component_design,
    'data_model': data_model,
    'implementation_phases': [
        {'phase': 1, 'tasks': [...], 'duration': '3 days'},
        {'phase': 2, 'tasks': [...], 'duration': '5 days'},
        {'phase': 3, 'tasks': [...], 'duration': '4 days'}
    ],
    'risks': [...],
    'recommendations': [...]
}

# Write to outbox
write('outbox/ARCHITECTURE_PLAN.md', format_plan(plan))

# Archive task
archive_file('inbox/ARCHITECTURE_TASK.md')
```

*Step 4: CHAD_YI Retrieval and Reporting*
```python
# Check Brain outbox
plan = read_plan('agents/cerebronn/outbox/ARCHITECTURE_PLAN.md')

# Format for human (summarized)
summary = f"""
📋 ARCHITECTURE PLAN COMPLETE

Overview: {plan.overview}
Tech Stack: {plan.tech_stack}
Timeline: {plan.total_duration}

The complete plan is available. Would you like me to:
1. Show the full plan
2. Summarize key decisions
3. Start implementation with Forger
"""

# Send to human
send_message(summary)
```

*Step 5: Human Decision*
```
Caleb: "Show me the key decisions"
```

*Step 6: CHAD_YI Detailed Report*
```python
# Extract key decisions
decisions = extract_key_decisions(plan)

# Format detailed report
report = format_decisions_report(decisions)

# Send to human
send_message(report)
```

### 2.4 The Workforce (Specialized Agents) Patterns

**Agent Design Principles:**

**1. Single Responsibility:**
Each agent should do one thing well. Helios audits. Forger builds. Quanta trades (suggests). Don't combine responsibilities.

**2. Stateless Operation:**
Agents should not maintain state in memory. All state should be stored in files. This enables:
- Restart without data loss
- Multiple instances (if needed)
- Easy debugging

**3. Idempotent Operations:**
Running an agent multiple times should not cause problems. If an agent sees a task it's already processed, it should skip it.

**4. Clear Input/Output:**
Every agent should have clear:
- Input format (what tasks look like)
- Output format (what results look like)
- Error format (how errors are reported)

**5. Graceful Degradation:**
Agents should handle failures gracefully:
- If a dependency is unavailable, log and retry
- If a task is malformed, report error and continue
- If system resources are low, reduce frequency

**Common Workforce Agent Patterns:**

**Pattern 1: Poll-Execute-Report**
```python
class PollingAgent:
    def __init__(self, inbox_dir, outbox_dir, sleep_interval=60):
        self.inbox_dir = inbox_dir
        self.outbox_dir = outbox_dir
        self.sleep_interval = sleep_interval
    
    def run(self):
        while True:
            self.process_inbox()
            time.sleep(self.sleep_interval)
    
    def process_inbox(self):
        for task_file in self.list_inbox_files():
            if self.is_processed(task_file):
                continue
            
            try:
                task = self.read_task(task_file)
                result = self.execute_task(task)
                self.write_result(result)
                self.mark_processed(task_file)
            except Exception as e:
                self.write_error(task, e)
                self.mark_processed(task_file)
    
    def execute_task(self, task):
        raise NotImplementedError
```

**Pattern 2: Event-Driven (File Watch)**
```python
class FileWatchAgent:
    def __init__(self, watch_dir):
        self.watch_dir = watch_dir
        self.observer = Observer()
    
    def run(self):
        handler = TaskHandler(self)
        self.observer.schedule(handler, self.watch_dir)
        self.observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        
        self.observer.join()
    
    def on_task_created(self, task_file):
        task = self.read_task(task_file)
        result = self.execute_task(task)
        self.write_result(result)
```

**Pattern 3: Scheduled (Cron-Based)**
```python
class ScheduledAgent:
    def __init__(self, schedule):
        self.schedule = schedule
    
    def run(self):
        while True:
            if self.should_run():
                self.execute()
            
            time.sleep(self.schedule.interval)
    
    def should_run(self):
        now = datetime.now()
        return self.schedule.matches(now)
    
    def execute(self):
        raise NotImplementedError
```



## CHAPTER 3: SKILL ARCHITECTURE PATTERNS FROM 54 LOCAL SKILLS

### 3.1 Skill Taxonomy Analysis

Based on analysis of 54 installed skills at `~/.npm-global/lib/node_modules/openclaw/skills/`, I've identified distinct architectural patterns:

**Category 1: CLI Wrapper Skills (Bash-First Pattern)**

Skills in this category wrap existing command-line tools:
- `apple-notes` wraps `memo` CLI
- `apple-reminders` wraps `remindctl` CLI  
- `bear-notes` wraps `grizzly` CLI
- `obsidian` wraps `obsidian-cli`
- `github` wraps `gh` CLI
- `tmux` wraps `tmux`

**Pattern Characteristics:**
```yaml
name: cli-wrapper-skill
description: "Wraps existing CLI tool for OpenClaw integration"
metadata:
  requires:
    bins: ["wrapped-cli-tool"]
  install:
    - kind: brew
      formula: "tool-package"
```

**Why This Pattern Works:**
1. **Leverages existing tools** - Don't reinvent the wheel
2. **Battle-tested** - CLI tools are already reliable
3. **Familiar interface** - Users already know the CLI
4. **Easy to debug** - Can test CLI independently
5. **Community support** - Existing documentation and community

**Implementation Example - Apple Notes:**
```markdown
# Apple Notes CLI

Use `memo notes` to manage Apple Notes directly from the terminal.

Setup
- Install (Homebrew): `brew tap antoniorodr/memo && brew install antoniorodr/memo/memo`
- Manual (pip): `pip install .` (after cloning the repo)
- macOS-only; if prompted, grant Automation access to Notes.app.

View Notes
- List all notes: `memo notes`
- Filter by folder: `memo notes -f "Folder Name"`
- Search notes (fuzzy): `memo notes -s "query"`

Create Notes
- Add a new note: `memo notes -a`
  - Opens an interactive editor to compose the note.
- Quick add with title: `memo notes -a "Note Title"`

Limitations
- Cannot edit notes containing images or attachments.
- Interactive prompts may require terminal access.
```

**Category 2: PTY Mode Skills (Interactive CLI Pattern)**

Skills requiring pseudo-terminal access for interactive applications:
- `coding-agent` - Codex, Claude Code, Pi agents
- `tmux` - tmux session control
- `1password` - `op` CLI (requires tmux for auth)

**Critical Pattern: PTY Mode Required**
```bash
# ✅ Correct - with PTY
bash pty:true command:"codex exec 'Your prompt'"

# ❌ Wrong - no PTY, agent may break
bash command:"codex exec 'Your prompt'"
```

**Why PTY Mode Matters:**
Interactive terminal applications (like Codex, Claude Code, tmux) require a pseudo-terminal to work correctly. Without PTY:
- Broken output (missing colors, formatting)
- Applications hang waiting for terminal input
- Cursor control doesn't work
- Terminal size detection fails

**Implementation from coding-agent SKILL.md:**
```markdown
## ⚠️ PTY Mode Required!

Coding agents (Codex, Claude Code, Pi) are **interactive terminal applications** that need a pseudo-terminal (PTY) to work correctly. Without PTY, you'll get broken output, missing colors, or the agent may hang.

**Always use `pty:true`** when running coding agents:

```bash
# ✅ Correct - with PTY
bash pty:true command:"codex exec 'Your prompt'"

# ❌ Wrong - no PTY, agent may break
bash command:"codex exec 'Your prompt'"
```

### Bash Tool Parameters

| Parameter    | Type    | Description                                                                 |
| ------------ | ------- | --------------------------------------------------------------------------- |
| `command`    | string  | The shell command to run                                                    |
| `pty`        | boolean | **Use for coding agents!** Allocates a pseudo-terminal for interactive CLIs |
| `workdir`    | string  | Working directory (agent sees only this folder's context)                   |
| `background` | boolean | Run in background, returns sessionId for monitoring                         |
| `timeout`    | number  | Timeout in seconds (kills process on expiry)                                |
| `elevated`   | boolean | Run on host instead of sandbox (if allowed)                                 |
```

**Category 3: API Integration Skills**

Skills that integrate with web APIs:
- `notion` - Notion API
- `trello` - Trello REST API
- `discord` - Discord API via message tool
- `github` - GitHub API via `gh` CLI

**Pattern Characteristics:**
```yaml
metadata:
  requires:
    env: ["API_KEY"]
    bins: ["curl", "jq"]
```

**Implementation from notion SKILL.md:**
```markdown
# notion

Use the Notion API to create/read/update pages, data sources (databases), and blocks.

## Setup

1. Create an integration at https://notion.so/my-integrations
2. Copy the API key (starts with `ntn_` or `secret_`)
3. Store it:

```bash
mkdir -p ~/.config/notion
echo "ntn_your_key_here" > ~/.config/notion/api_key
```

4. Share target pages/databases with your integration

## API Basics

All requests need:

```bash
NOTION_KEY=$(cat ~/.config/notion/api_key)
curl -X GET "https://api.notion.com/v1/..." \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json"
```
```

**Category 4: Local AI Skills**

Skills that run AI models locally:
- `openai-whisper` - Local speech-to-text
- `sherpa-onnx-tts` - Local text-to-speech
- `openai-image-gen` - Local image generation

**Pattern: Local Processing, No API Key**
```markdown
# Whisper (CLI)

Use `whisper` to transcribe audio locally.

Quick start
- `whisper /path/audio.mp3 --model medium --output_format txt --output_dir .`
- `whisper /path/audio.m4a --task translate --output_format srt`

Notes
- Models download to `~/.cache/whisper` on first run
- `--model` defaults to `turbo` on this install
- Use smaller models for speed, larger for accuracy
```

**Category 5: Security/Authentication Skills**

Skills handling sensitive operations:
- `1password` - 1Password CLI integration
- `healthcheck` - Security auditing

**Critical Pattern: T-Max Sessions for Secrets**
```markdown
## REQUIRED tmux session (T-Max)

The shell tool uses a fresh TTY per command. To avoid re-prompts and failures, always run `op` inside a dedicated tmux session with a fresh socket/session name.

Example:
```bash
SOCKET_DIR="${OPENCLAW_TMUX_SOCKET_DIR:-${TMPDIR:-/tmp}/openclaw-tmux-sockets}"
mkdir -p "$SOCKET_DIR"
SOCKET="$SOCKET_DIR/openclaw-op.sock"
SESSION="op-auth-$(date +%Y%m%d-%H%M%S)"

tmux -S "$SOCKET" new -d -s "$SESSION" -n shell
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- "op signin --account my.1password.com" Enter
tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":0.0 -S -200
tmux -S "$SOCKET" kill-session -t "$SESSION"
```

## Guardrails

- Never paste secrets into logs, chat, or code
- Prefer `op run` / `op inject` over writing secrets to disk
```

**Category 6: Canvas/Tailscale Skills**

Skills for visual output and networking:
- `canvas` - HTML display on connected nodes

**Architecture:**
```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│  Canvas Host    │────▶│   Node Bridge    │────▶│  Node App   │
│  (HTTP Server)  │     │  (TCP Server)    │     │ (Mac/iOS/   │
│  Port 18793     │     │  Port 18790      │     │  Android)   │
└─────────────────┘     └──────────────────┘     └─────────────┘
```

**Tailscale Integration:**
```markdown
### Tailscale Integration

The canvas host server binds based on `gateway.bind` setting:

| Bind Mode  | Server Binds To     | Canvas URL Uses            |
| ---------- | ------------------- | -------------------------- |
| `loopback` | 127.0.0.1           | localhost (local only)     |
| `lan`      | LAN interface       | LAN IP address             |
| `tailnet`  | Tailscale interface | Tailscale hostname         |
| `auto`     | Best available      | Tailscale > LAN > loopback |

**Key insight:** The `canvasHostHostForBridge` is derived from `bridgeHost`. When bound to Tailscale, nodes receive URLs like:

```
http://<tailscale-hostname>:18793/__openclaw__/canvas/<file>.html
```
```

### 3.2 Skill Creation Best Practices

From analysis of `skill-creator/SKILL.md`:

**Core Principles:**

**1. Concise is Key:**
```markdown
The context window is a public good. Skills share the context window with everything else Codex needs: system prompt, conversation history, other Skills' metadata, and the actual user request.

**Default assumption: Codex is already very smart.** Only add context Codex doesn't already have.
```

**2. Set Appropriate Degrees of Freedom:**
```markdown
**High freedom (text-based instructions)**: Use when multiple approaches are valid
**Medium freedom (pseudocode/scripts with parameters)**: Use when a preferred pattern exists
**Low freedom (specific scripts, few parameters)**: Use when operations are fragile
```

**3. Progressive Disclosure Design:**
```markdown
Skills use a three-level loading system:
1. **Metadata (name + description)** - Always in context (~100 words)
2. **SKILL.md body** - When skill triggers (<5k words)
3. **Bundled resources** - As needed by Codex (unlimited)
```

**Skill Directory Structure:**
```
skill-name/
├── SKILL.md                 # Required - main documentation
├── README.md                # Optional - detailed guide
├── scripts/                 # Executable code
│   └── helper.py
├── references/              # Reference material
│   ├── api-docs.md
│   └── examples.md
├── assets/                  # Output resources
│   ├── templates/
│   └── icons/
└── config/
    └── default.conf
```

**SKILL.md Frontmatter Format:**
```yaml
---
name: skill-name
description: "Clear description of what this skill does and when to use it"
homepage: https://example.com
metadata:
  openclaw:
    emoji: "🔧"
    requires:
      bins: ["required-binary"]
      env: ["REQUIRED_ENV_VAR"]
      config: ["config.key"]
    install:
      - id: brew
        kind: brew
        formula: "package-name"
        bins: ["binary-name"]
        label: "Install via Homebrew"
      - id: apt
        kind: apt
        package: "package-name"
        bins: ["binary-name"]
        label: "Install via apt"
allowed-tools: ["tool1", "tool2"]
---
```

---

## CHAPTER 4: THE $10K FAILURE - COMPLETE CASE STUDY

### 4.1 Timeline of Events

**Month 1: Initial Success**
- File-based system working correctly
- Quanta trading bot functioning with approval workflow
- Simple architecture: signal → proposal → approval → execution

**Month 2: The Pivot to Complexity**
- Attempted to add "real-time" capabilities
- Introduced WebSocket infrastructure
- Added TCP socket communication between agents
- Implemented ACP (Agent Communication Protocol)
- Built SQLite database for "better" tracking
- Added Redis for caching

**Day X: First Failure**
- Quanta tracking system stopped working
- Two trades opened without proper state tracking
- State sync between OANDA and Quanta failed
- Partial close system didn't apply to untracked trades

**Day X+2: Discovery**
- Human discovered untracked trades
- Trades had moved against position
- Loss: $10,000

**Current: Complete Re-evaluation**
- All complex infrastructure removed
- Return to file-based architecture
- Rebuilding with lessons learned

### 4.2 Technical Analysis of Failures

**Failure 1: WebSocket Infrastructure**

*What Was Built:*
```python
class WebSocketServer:
    def __init__(self, port=8765):
        self.port = port
        self.clients = set()
    
    async def handle_client(self, websocket, path):
        self.clients.add(websocket)
        try:
            async for message in websocket:
                await self.process_message(message)
        finally:
            self.clients.remove(websocket)
    
    async def broadcast(self, message):
        for client in self.clients:
            await client.send(message)
```

*Why It Failed:*
1. **Library incompatibility** - Python websockets version conflicts
2. **Connection drops** - Agents disconnected, didn't reconnect properly
3. **State synchronization** - Complex state management required
4. **Debugging difficulty** - Hard to trace message flow
5. **Overkill** - File-based polling was sufficient

*The Lesson:*
Don't build what you don't need. The requirement was "track trades," not "real-time updates." A cron job checking every minute would have been sufficient.

**Failure 2: Autonomous Execution**

*What Was Built:*
```python
class QuantaTradingBot:
    async def on_signal(self, signal):
        # BAD: No approval checkpoint
        trade = await self.execute_trade(signal)
        await self.update_dashboard(trade)
```

*What Should Have Been Built:*
```python
class QuantaTradingBot:
    async def on_signal(self, signal):
        # GOOD: Proposal with approval
        proposal = self.create_proposal(signal)
        await self.write_to_chad_yi_inbox(proposal)
        
        # Wait for approval
        approval = await self.wait_for_approval()
        if approval:
            trade = await self.execute_trade(signal)
            await self.record_trade(trade)
```

*The Lesson:*
Never auto-execute financial transactions. Human approval is non-negotiable.

**Failure 3: Broken State Tracking**

*What Was Built:*
```python
# Multiple state sources
state = {
    'sqlite': read_from_sqlite(),
    'redis': read_from_redis(),
    'oanda': await self.oanda.get_positions(),
    'memory': self.memory_state
}

# Which one is truth?
```

*What Should Have Been Built:*
```python
# Single source of truth
trades = read_from_sqlite()
# Sync with OANDA periodically
await sync_with_oanda()
# SQLite is always authoritative
```

*The Lesson:*
Multiple state sources create confusion. Have one authoritative source.

**Failure 4: False Confidence**

*What Was Claimed:*
"Quanta is working! The system is fixed!"

*What Was True:*
Quanta was running (process existed), but:
- Tracking wasn't working
- State sync was broken
- Partial closes weren't applying
- No end-to-end test passed

*The Lesson:*
"Running" ≠ "Working". Test functionality, not just startup.

### 4.3 What Should Have Been Done

**Architecture - Simple File-Based:**
```
Signal Detected
    ↓
Quanta writes proposal to /agents/chad-yi/inbox/
    ↓
CHAD_YI reads, presents to human
    ↓
Human approves (YES)
    ↓
CHAD_YI writes approval to /agents/quanta/inbox/
    ↓
Quanta reads approval, executes
    ↓
Quanta writes result to /agents/chad-yi/outbox/
    ↓
CHAD_YI reports to human
    ↓
Quanta updates SQLite (single source of truth)
```

**Risk Management - Strict Rules:**
```python
# Position sizing based on risk
MAX_RISK_PERCENT = 0.02  # 2% per trade
DAILY_LOSS_LIMIT = 0.06   # 6% daily

def calculate_position_size(account_balance, risk_percent, stop_loss_pips, pip_value):
    risk_amount = account_balance * risk_percent
    position_size = risk_amount / (stop_loss_pips * pip_value)
    return int(position_size)

# Example with $1,750 account
account = 1750
risk = 0.02
stop_loss = 100
pip_value = 0.10

units = calculate_position_size(account, risk, stop_loss, pip_value)
# Result: 3.5 units → 3 units
# Risk: $30 (2% of $1,750) - CORRECT
```

**Tracking - SQLite with Reconciliation:**
```python
class TradeTracker:
    def __init__(self, db_path='trades.db'):
        self.db = sqlite3.connect(db_path)
        self.create_tables()
    
    def record_trade(self, trade):
        """Record trade in database - single source of truth"""
        self.db.execute('''
            INSERT INTO trades (id, symbol, direction, entry, stop_loss, size, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (trade.id, trade.symbol, trade.direction, 
              trade.entry, trade.stop_loss, trade.size, 'OPEN'))
        self.db.commit()
    
    async def reconcile_with_oanda(self):
        """Sync database with OANDA - catch discrepancies"""
        db_trades = self.get_open_trades()
        oanda_positions = await self.oanda.get_positions()
        
        for trade in db_trades:
            if trade.id not in oanda_positions:
                # Discrepancy! Alert human.
                await self.alert_discrepancy(trade)
```

### 4.4 Lessons Learned Summary

**Technical Lessons:**
1. **Complexity kills reliability** - Every component is a potential failure point
2. **File-based > real-time** - Simple and reliable beats fast and fragile
3. **Single source of truth** - Multiple state sources create confusion
4. **Test end-to-end** - Verify functionality, not just startup

**Process Lessons:**
1. **Verify before claiming** - "Running" ≠ "Working"
2. **Human approval mandatory** - Never auto-execute financial transactions
3. **Document failure modes** - Know what can go wrong
4. **Start simple, add complexity only when needed**

**Organizational Lessons:**
1. **Transparency** - Admit failures immediately
2. **No overpromising** - Be honest about capabilities
3. **Debt acknowledgment** - The $1M debt represents real system failures
4. **Partnership model** - Human and AI working together

---

[CONTINUING TO EXPAND WITH DASHBOARD ARCHITECTURES, OPERATIONAL PATTERNS, AND CASE STUDIES...]


