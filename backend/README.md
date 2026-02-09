# Mission Control Dashboard API

FastAPI backend with WebSocket support for real-time mission control dashboard.

## Features

- ✅ RESTful API endpoints for Sessions, Cron Jobs, Agents, Projects, and Stats
- ✅ WebSocket support via Socket.IO for real-time updates
- ✅ CORS enabled for frontend integration
- ✅ Pydantic models for data validation
- ✅ In-memory data store with sample seed data
- ✅ Auto-broadcasting updates every 5 seconds

## Installation

```bash
# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Server

```bash
# Standard run
uvicorn main:app --reload

# Or with specific host/port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Sessions
- `GET /api/sessions` - List all sessions
- `GET /api/sessions/{id}` - Get specific session
- `POST /api/sessions` - Create session
- `PUT /api/sessions/{id}` - Update session
- `DELETE /api/sessions/{id}` - Delete session

### Cron Jobs
- `GET /api/cron-jobs` - List all cron jobs
- `GET /api/cron-jobs/{id}` - Get specific cron job
- `POST /api/cron-jobs` - Create cron job
- `PUT /api/cron-jobs/{id}` - Update cron job
- `DELETE /api/cron-jobs/{id}` - Delete cron job
- `POST /api/cron-jobs/{id}/toggle` - Toggle enabled status

### Agents
- `GET /api/agents` - List all agents
- `GET /api/agents/{id}` - Get specific agent
- `POST /api/agents` - Create agent
- `PUT /api/agents/{id}` - Update agent
- `DELETE /api/agents/{id}` - Delete agent
- `POST /api/agents/{id}/heartbeat` - Update heartbeat
- `POST /api/agents/{id}/status` - Update status

### Projects
- `GET /api/projects` - List all projects
- `GET /api/projects/{id}` - Get specific project
- `POST /api/projects` - Create project
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project
- `POST /api/projects/{id}/progress` - Update progress

### Stats
- `GET /api/stats` - Get dashboard statistics
- `GET /api/stats/detailed` - Get detailed statistics

### Health
- `GET /health` - Health check
- `GET /` - API info

## WebSocket Events

### Client -> Server
- `connect` - Client connection
- `disconnect` - Client disconnection
- `subscribe` - Subscribe to channels: `{channels: ['agents', 'sessions']}`
- `unsubscribe` - Unsubscribe from channels
- `heartbeat` - Send heartbeat

### Server -> Client
- `connected` - Connection acknowledgment
- `stats_update` - Periodic stats update (every 5s)
- `agents_update` - Agents status update
- `sessions_update` - Sessions status update
- `{resource}_changed` - Real-time change notifications
- `heartbeat_ack` - Heartbeat acknowledgment

### Example WebSocket Client (JavaScript)

```javascript
const socket = io('ws://localhost:8000');

socket.on('connect', () => {
  console.log('Connected:', socket.id);
  
  // Subscribe to channels
  socket.emit('subscribe', { channels: ['agents', 'sessions'] });
});

socket.on('stats_update', (data) => {
  console.log('Stats:', data);
});

socket.on('agents_update', (data) => {
  console.log('Agents:', data);
});

socket.on('sessions_update', (data) => {
  console.log('Sessions:', data);
});
```

## Interactive Docs

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Architecture

```
┌─────────────────────────────────────┐
│         FastAPI App                 │
│  ┌─────────────────────────────┐   │
│  │     Socket.IO Server        │   │
│  │  - Real-time updates        │   │
│  │  - Channel subscriptions    │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │      REST Endpoints         │   │
│  │  - /api/sessions            │   │
│  │  - /api/cron-jobs           │   │
│  │  - /api/agents              │   │
│  │  - /api/projects            │   │
│  │  - /api/stats               │   │
│  └─────────────────────────────┘   │
│  ┌─────────────────────────────┐   │
│  │     Data Store (In-Mem)     │   │
│  │  - Sessions, Jobs, Agents   │   │
│  │  - Projects, Stats          │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```
