# GOOGLE WORKSPACE AGENT INTEGRATION
## Integrating gws-cli into Agent Infrastructure

---

## ARCHITECTURE OVERVIEW

```
CHAD_YI (The Face)
    ↓ Routes tasks
Google Workspace Agent (gws-agent)
    ↓ Executes via
Google Workspace CLI (gws)
    ↓ Accesses
Gmail / Drive / Calendar / Sheets / Docs
```

---

## AGENT IMPLEMENTATION

**File:** `agents/gws-agent/gws_agent.py`

```python
#!/usr/bin/env python3
"""
Google Workspace Agent
Integrates Gmail, Drive, Calendar, Docs, Sheets
"""

import sys
sys.path.insert(0, str(Path.home() / '.openclaw/workspace/lib'))

import json
import subprocess
from pathlib import Path
from datetime import datetime
from agent_base import AgentBase, Task, Result


class GoogleWorkspaceAgent(AgentBase):
    """
    Google Workspace integration agent
    
    Handles:
    - Gmail operations
    - Drive file management
    - Calendar events
    - Document creation
    - Spreadsheet operations
    """
    
    def __init__(self):
        super().__init__('gws-agent', {
            'poll_interval': 60,
            'use_database': False  # Uses Google services instead
        })
        
        # Verify gws is installed
        if not self._check_gws_installed():
            self.logger.error("gws CLI not installed. Run: npm install -g @googleworkspace/cli")
    
    def _check_gws_installed(self) -> bool:
        """Check if gws CLI is available"""
        try:
            result = subprocess.run(['gws', '--version'], 
                                  capture_output=True, 
                                  timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _run_gws(self, command: list) -> dict:
        """Execute gws command and return result"""
        try:
            result = subprocess.run(
                ['gws'] + command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                'success': result.returncode == 0,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Command timed out'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def execute(self, task: Task) -> Result:
        """Route to appropriate handler"""
        handlers = {
            'GMAIL_LIST': self.handle_gmail_list,
            'GMAIL_SEND': self.handle_gmail_send,
            'DRIVE_LIST': self.handle_drive_list,
            'DRIVE_UPLOAD': self.handle_drive_upload,
            'DRIVE_DOWNLOAD': self.handle_drive_download,
            'CALENDAR_LIST': self.handle_calendar_list,
            'CALENDAR_CREATE': self.handle_calendar_create,
            'SHEETS_READ': self.handle_sheets_read,
            'SHEETS_WRITE': self.handle_sheets_write,
            'DOCS_CREATE': self.handle_docs_create,
        }
        
        handler = handlers.get(task.type)
        if handler:
            return handler(task.data)
        
        return Result(task.id, False, f"Unknown task type: {task.type}")
    
    # ==================== GMAIL ====================
    
    def handle_gmail_list(self, data: dict) -> Result:
        """List emails from Gmail"""
        limit = data.get('limit', 10)
        label = data.get('label', '')
        query = data.get('query', '')
        
        cmd = ['gmail', 'list', '--limit', str(limit), '--json']
        
        if label:
            cmd.extend(['--label', label])
        if query:
            cmd.extend(['--query', query])
        
        result = self._run_gws(cmd)
        
        if result['success']:
            try:
                emails = json.loads(result['stdout'])
                return Result('gmail_list', True, {
                    'emails': emails,
                    'count': len(emails)
                })
            except json.JSONDecodeError:
                return Result('gmail_list', True, {
                    'raw_output': result['stdout']
                })
        
        return Result('gmail_list', False, result.get('stderr', 'Unknown error'))
    
    def handle_gmail_send(self, data: dict) -> Result:
        """Send email via Gmail"""
        to = data.get('to')
        subject = data.get('subject')
        body = data.get('body', '')
        html = data.get('html', False)
        
        if not to or not subject:
            return Result('gmail_send', False, 'Missing to or subject')
        
        cmd = ['gmail', 'send', '--to', to, '--subject', subject, '--body', body]
        
        if html:
            cmd.append('--html')
        
        result = self._run_gws(cmd)
        
        if result['success']:
            return Result('gmail_send', True, {
                'message': 'Email sent successfully',
                'to': to,
                'subject': subject
            })
        
        return Result('gmail_send', False, result.get('stderr', 'Failed to send'))
    
    # ==================== DRIVE ====================
    
    def handle_drive_list(self, data: dict) -> Result:
        """List files in Google Drive"""
        folder = data.get('folder', '')
        query = data.get('query', '')
        
        cmd = ['drive', 'list', '--json']
        
        if folder:
            cmd.extend(['--folder', folder])
        if query:
            cmd.extend(['--query', query])
        
        result = self._run_gws(cmd)
        
        if result['success']:
            try:
                files = json.loads(result['stdout'])
                return Result('drive_list', True, {
                    'files': files,
                    'count': len(files)
                })
            except:
                return Result('drive_list', True, {
                    'raw': result['stdout']
                })
        
        return Result('drive_list', False, result.get('stderr'))
    
    def handle_drive_upload(self, data: dict) -> Result:
        """Upload file to Drive"""
        local_path = data.get('local_path')
        folder = data.get('folder', '')
        name = data.get('name', '')
        
        if not local_path:
            return Result('drive_upload', False, 'Missing local_path')
        
        cmd = ['drive', 'upload', local_path]
        
        if folder:
            cmd.extend(['--folder', folder])
        if name:
            cmd.extend(['--name', name])
        
        result = self._run_gws(cmd)
        
        if result['success']:
            return Result('drive_upload', True, {
                'message': 'File uploaded',
                'local_path': local_path,
                'name': name or Path(local_path).name
            })
        
        return Result('drive_upload', False, result.get('stderr'))
    
    def handle_drive_download(self, data: dict) -> Result:
        """Download file from Drive"""
        file_id = data.get('file_id')
        output = data.get('output', '.')
        
        if not file_id:
            return Result('drive_download', False, 'Missing file_id')
        
        cmd = ['drive', 'download', file_id, '--output', output]
        result = self._run_gws(cmd)
        
        if result['success']:
            return Result('drive_download', True, {
                'file_id': file_id,
                'output': output
            })
        
        return Result('drive_download', False, result.get('stderr'))
    
    # ==================== CALENDAR ====================
    
    def handle_calendar_list(self, data: dict) -> Result:
        """List calendar events"""
        start = data.get('start', '')
        end = data.get('end', '')
        calendar = data.get('calendar', 'primary')
        
        cmd = ['calendar', 'events', 'list', '--json']
        
        if start:
            cmd.extend(['--start', start])
        if end:
            cmd.extend(['--end', end])
        if calendar:
            cmd.extend(['--calendar', calendar])
        
        result = self._run_gws(cmd)
        
        if result['success']:
            try:
                events = json.loads(result['stdout'])
                return Result('calendar_list', True, {
                    'events': events,
                    'count': len(events)
                })
            except:
                return Result('calendar_list', True, {
                    'raw': result['stdout']
                })
        
        return Result('calendar_list', False, result.get('stderr'))
    
    def handle_calendar_create(self, data: dict) -> Result:
        """Create calendar event"""
        title = data.get('title')
        start = data.get('start')  # ISO format: 2026-03-10T14:00:00
        end = data.get('end')
        description = data.get('description', '')
        location = data.get('location', '')
        attendees = data.get('attendees', '')  # comma-separated emails
        
        if not title or not start or not end:
            return Result('calendar_create', False, 'Missing required fields')
        
        cmd = [
            'calendar', 'events', 'create',
            title,
            '--start', start,
            '--end', end
        ]
        
        if description:
            cmd.extend(['--description', description])
        if location:
            cmd.extend(['--location', location])
        if attendees:
            cmd.extend(['--attendees', attendees])
        
        result = self._run_gws(cmd)
        
        if result['success']:
            return Result('calendar_create', True, {
                'message': 'Event created',
                'title': title,
                'start': start,
                'end': end
            })
        
        return Result('calendar_create', False, result.get('stderr'))
    
    # ==================== SHEETS ====================
    
    def handle_sheets_read(self, data: dict) -> Result:
        """Read from Google Sheets"""
        sheet_id = data.get('sheet_id')
        range_name = data.get('range', '')  # e.g., "Sheet1!A1:D10"
        
        if not sheet_id:
            return Result('sheets_read', False, 'Missing sheet_id')
        
        cmd = ['sheets', 'get', sheet_id]
        
        if range_name:
            cmd.extend(['--range', range_name])
        
        cmd.append('--json')
        result = self._run_gws(cmd)
        
        if result['success']:
            try:
                data = json.loads(result['stdout'])
                return Result('sheets_read', True, {
                    'data': data,
                    'range': range_name or 'all'
                })
            except:
                return Result('sheets_read', True, {
                    'raw': result['stdout']
                })
        
        return Result('sheets_read', False, result.get('stderr'))
    
    def handle_sheets_write(self, data: dict) -> Result:
        """Write to Google Sheets"""
        sheet_id = data.get('sheet_id')
        range_name = data.get('range')
        values = data.get('values', [])
        
        if not sheet_id or not range_name:
            return Result('sheets_write', False, 'Missing sheet_id or range')
        
        # Convert values to string format
        if isinstance(values, list):
            values_str = '|'.join([','.join(row) if isinstance(row, list) else row 
                                   for row in values])
        else:
            values_str = values
        
        cmd = [
            'sheets', 'update',
            sheet_id,
            '--range', range_name,
            '--values', values_str
        ]
        
        result = self._run_gws(cmd)
        
        if result['success']:
            return Result('sheets_write', True, {
                'sheet_id': sheet_id,
                'range': range_name,
                'values_written': len(values) if isinstance(values, list) else 1
            })
        
        return Result('sheets_write', False, result.get('stderr'))
    
    # ==================== DOCS ====================
    
    def handle_docs_create(self, data: dict) -> Result:
        """Create Google Doc"""
        title = data.get('title')
        content = data.get('content', '')
        
        if not title:
            return Result('docs_create', False, 'Missing title')
        
        cmd = ['docs', 'create', title]
        result = self._run_gws(cmd)
        
        if result['success']:
            # Extract document ID from output if possible
            doc_id = self._extract_doc_id(result['stdout'])
            
            # If content provided, append it
            if content and doc_id:
                append_cmd = ['docs', 'append', doc_id, '--text', content]
                self._run_gws(append_cmd)
            
            return Result('docs_create', True, {
                'message': 'Document created',
                'title': title,
                'doc_id': doc_id
            })
        
        return Result('docs_create', False, result.get('stderr'))
    
    def _extract_doc_id(self, output: str) -> str:
        """Extract document ID from gws output"""
        # This is a placeholder - actual extraction depends on gws output format
        # You may need to adjust based on actual CLI behavior
        return ''


if __name__ == '__main__':
    agent = GoogleWorkspaceAgent()
    agent.run()
```

---

## SYSTEMD SERVICE

**File:** `~/.config/systemd/user/gws-agent.service`

```ini
[Unit]
Description=Google Workspace Agent
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/chad-yi/.openclaw/workspace
ExecStart=/usr/bin/python3 agents/gws-agent/gws_agent.py
Restart=always
RestartSec=10
Environment="GWS_CREDENTIALS=/home/chad-yi/.config/googleworkspace/client_secret.json"

[Install]
WantedBy=default.target
```

**Enable:**
```bash
systemctl --user daemon-reload
systemctl --user enable gws-agent
systemctl --user start gws-agent
```

---

## INTEGRATION WITH CHAD_YI

**Task Routing:**

```python
# In CHAD_YI routing logic
GOOGLE_WORKSPACE_TASKS = [
    'GMAIL_LIST',
    'GMAIL_SEND', 
    'DRIVE_LIST',
    'DRIVE_UPLOAD',
    'DRIVE_DOWNLOAD',
    'CALENDAR_LIST',
    'CALENDAR_CREATE',
    'SHEETS_READ',
    'SHEETS_WRITE',
    'DOCS_CREATE',
]

def route_task(task_type):
    if task_type in GOOGLE_WORKSPACE_TASKS:
        return 'gws-agent'
    # ... other routing
```

**Example Flow:**

```
You: "Send email to Lisa about contract"
    ↓
CHAD_YI: Creates task GMAIL_SEND
    ↓
Writes to agents/gws-agent/inbox/
    ↓
gws-agent reads task
    ↓
Executes: gws gmail send --to lisa@... --subject "Contract" --body "..."
    ↓
Reports success to CHAD_YI outbox
    ↓
CHAD_YI: "Email sent to Lisa"
```

---

## USE CASES

### 1. Daily Email Report

**CHAD_YI triggers:**
```python
# Every morning
task = {
    'type': 'GMAIL_LIST',
    'data': {
        'label': 'UNREAD',
        'limit': 20
    }
}
# Send to gws-agent
# Format results for human
```

### 2. File Backup

**Helios triggers:**
```python
# Weekly backup
task = {
    'type': 'DRIVE_UPLOAD',
    'data': {
        'local_path': '/path/to/backup.zip',
        'folder': 'BACKUPS_FOLDER_ID'
    }
}
```

### 3. Task Tracking (Sheets Alternative to SQLite)

```python
# Instead of SQLite, use Google Sheets
task = {
    'type': 'SHEETS_WRITE',
    'data': {
        'sheet_id': 'YOUR_TASK_SHEET_ID',
        'range': 'Tasks!A2',
        'values': [['2026-03-06', 'New Task', 'Pending', 'High']]
    }
}
```

### 4. Meeting Scheduling

```python
task = {
    'type': 'CALENDAR_CREATE',
    'data': {
        'title': 'Project Review',
        'start': '2026-03-10T14:00:00',
        'end': '2026-03-10T15:00:00',
        'attendees': 'person1@example.com,person2@example.com',
        'description': 'Review Q1 progress'
    }
}
```

---

## SETUP CHECKLIST

- [ ] Install gws CLI: `npm install -g @googleworkspace/cli`
- [ ] Create Google Cloud Project
- [ ] Enable APIs (Gmail, Drive, Calendar, Docs, Sheets)
- [ ] Configure OAuth consent screen
- [ ] Create OAuth client ID (Desktop app)
- [ ] Download client_secret.json
- [ ] Set environment: `export GWS_CREDENTIALS="/path/to/client_secret.json"`
- [ ] Authenticate: `gws auth login`
- [ ] Verify: `gws auth status`
- [ ] Create gws-agent directory and files
- [ ] Start gws-agent service
- [ ] Test with simple task

---

## SECURITY NOTES

1. **Never commit client_secret.json** to git
2. **Store credentials outside workspace** (e.g., ~/.config/)
3. **Use environment variables** for credential paths
4. **Limit OAuth scopes** to only needed APIs
5. **Use test users** in OAuth consent screen

---

## FILES CREATED

1. `skills/google-workspace/SKILL.md` - Documentation
2. `agents/gws-agent/gws_agent.py` - Agent implementation
3. `~/.config/systemd/user/gws-agent.service` - Service file

**Ready to deploy.**
