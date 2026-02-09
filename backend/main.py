"""
Mission Control Dashboard API
FastAPI backend with WebSocket support for real-time updates
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import socketio
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import asyncio
import json
import uuid

# ============================================
# Pydantic Models
# ============================================

class Session(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    status: str = Field(default="active")  # active, inactive, error
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    metadata: dict = Field(default_factory=dict)

class SessionCreate(BaseModel):
    name: str
    metadata: Optional[dict] = None

class CronJob(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    schedule: str  # cron expression
    command: str
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    status: str = Field(default="pending")  # pending, running, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CronJobCreate(BaseModel):
    name: str
    schedule: str
    command: str
    enabled: Optional[bool] = True

class Agent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str  # worker, scheduler, monitor, etc.
    status: str = Field(default="idle")  # idle, busy, error, offline
    capabilities: List[str] = Field(default_factory=list)
    last_heartbeat: Optional[datetime] = None
    tasks_completed: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AgentCreate(BaseModel):
    name: str
    type: str
    capabilities: Optional[List[str]] = None

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    status: str = Field(default="active")  # active, paused, completed, archived
    progress: float = Field(default=0.0, ge=0.0, le=100.0)
    tasks_total: int = 0
    tasks_completed: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None

class Stats(BaseModel):
    total_sessions: int
    active_sessions: int
    total_agents: int
    active_agents: int
    total_cron_jobs: int
    enabled_cron_jobs: int
    total_projects: int
    active_projects: int
    system_uptime: float  # seconds
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# ============================================
# In-Memory Data Store (replace with DB in production)
# ============================================

class DataStore:
    def __init__(self):
        self.sessions: dict[str, Session] = {}
        self.cron_jobs: dict[str, CronJob] = {}
        self.agents: dict[str, Agent] = {}
        self.projects: dict[str, Project] = {}
        self.start_time: datetime = datetime.utcnow()
        
        # Seed with sample data
        self._seed_data()
    
    def _seed_data(self):
        # Seed sessions
        for i in range(3):
            session = Session(
                name=f"Session-{i+1}",
                status="active" if i % 2 == 0 else "inactive",
                metadata={"env": "production" if i == 0 else "development"}
            )
            self.sessions[session.id] = session
        
        # Seed cron jobs
        cron_jobs_data = [
            ("Daily Backup", "0 2 * * *", "backup.sh"),
            ("Health Check", "*/5 * * * *", "health_check.py"),
            ("Report Generator", "0 9 * * 1", "generate_report.py"),
        ]
        for name, schedule, command in cron_jobs_data:
            job = CronJob(name=name, schedule=schedule, command=command)
            self.cron_jobs[job.id] = job
        
        # Seed agents
        agents_data = [
            ("Agent-Alpha", "worker", ["compute", "storage"]),
            ("Agent-Beta", "scheduler", ["queue", "timing"]),
            ("Agent-Gamma", "monitor", ["metrics", "alerts"]),
        ]
        for name, agent_type, caps in agents_data:
            agent = Agent(name=name, type=agent_type, capabilities=caps)
            agent.last_heartbeat = datetime.utcnow()
            self.agents[agent.id] = agent
        
        # Seed projects
        projects_data = [
            ("Mission Alpha", "Primary mission control project", 75.5),
            ("Infrastructure", "System infrastructure setup", 45.0),
            ("Data Pipeline", "ETL pipeline development", 90.0),
        ]
        for name, desc, progress in projects_data:
            project = Project(name=name, description=desc, progress=progress)
            project.tasks_total = 20
            project.tasks_completed = int(20 * progress / 100)
            self.projects[project.id] = project
    
    def get_stats(self) -> Stats:
        return Stats(
            total_sessions=len(self.sessions),
            active_sessions=sum(1 for s in self.sessions.values() if s.status == "active"),
            total_agents=len(self.agents),
            active_agents=sum(1 for a in self.agents.values() if a.status in ["idle", "busy"]),
            total_cron_jobs=len(self.cron_jobs),
            enabled_cron_jobs=sum(1 for c in self.cron_jobs.values() if c.enabled),
            total_projects=len(self.projects),
            active_projects=sum(1 for p in self.projects.values() if p.status == "active"),
            system_uptime=(datetime.utcnow() - self.start_time).total_seconds()
        )

data_store = DataStore()

# ============================================
# Socket.IO Setup
# ============================================

sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*'
)

# ============================================
# Lifespan Manager
# ============================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Mission Control Dashboard API starting up...")
    
    # Start background tasks
    task = asyncio.create_task(emit_periodic_updates())
    
    yield
    
    # Shutdown
    print("🛑 Mission Control Dashboard API shutting down...")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

# ============================================
# FastAPI App
# ============================================

app = FastAPI(
    title="Mission Control Dashboard API",
    description="Real-time dashboard API with WebSocket support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wrap with SocketIO
socket_app = socketio.ASGIApp(sio, app)

# ============================================
# Socket.IO Events
# ============================================

@sio.event
async def connect(sid, environ):
    print(f"🔌 Client connected: {sid}")
    await sio.emit('connected', {'sid': sid, 'message': 'Welcome to Mission Control!'}, room=sid)

@sio.event
async def disconnect(sid):
    print(f"🔌 Client disconnected: {sid}")

@sio.event
async def subscribe(sid, data):
    """Subscribe to specific data channels"""
    channels = data.get('channels', [])
    for channel in channels:
        await sio.enter_room(sid, channel)
    await sio.emit('subscribed', {'channels': channels}, room=sid)

@sio.event
async def unsubscribe(sid, data):
    """Unsubscribe from data channels"""
    channels = data.get('channels', [])
    for channel in channels:
        await sio.leave_room(sid, channel)
    await sio.emit('unsubscribed', {'channels': channels}, room=sid)

@sio.event
async def heartbeat(sid, data):
    """Client heartbeat"""
    await sio.emit('heartbeat_ack', {'timestamp': datetime.utcnow().isoformat()}, room=sid)

async def emit_periodic_updates():
    """Emit periodic updates to all connected clients"""
    while True:
        try:
            await asyncio.sleep(5)  # Update every 5 seconds
            
            # Emit stats update
            stats = data_store.get_stats()
            await sio.emit('stats_update', stats.model_dump(mode='json'))
            
            # Emit agents status
            agents_data = [a.model_dump(mode='json') for a in data_store.agents.values()]
            await sio.emit('agents_update', {'agents': agents_data}, room='agents')
            
            # Emit sessions status
            sessions_data = [s.model_dump(mode='json') for s in data_store.sessions.values()]
            await sio.emit('sessions_update', {'sessions': sessions_data}, room='sessions')
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error in periodic updates: {e}")

async def notify_change(event_type: str, data: dict):
    """Notify clients of data changes"""
    await sio.emit(f'{event_type}_changed', data)

# ============================================
# API Endpoints - Sessions
# ============================================

@app.get("/api/sessions", response_model=List[Session], tags=["Sessions"])
async def get_sessions():
    """Get all sessions"""
    return list(data_store.sessions.values())

@app.get("/api/sessions/{session_id}", response_model=Session, tags=["Sessions"])
async def get_session(session_id: str):
    """Get a specific session"""
    if session_id not in data_store.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    return data_store.sessions[session_id]

@app.post("/api/sessions", response_model=Session, tags=["Sessions"])
async def create_session(session: SessionCreate):
    """Create a new session"""
    new_session = Session(
        name=session.name,
        metadata=session.metadata or {}
    )
    data_store.sessions[new_session.id] = new_session
    await notify_change('sessions', {'action': 'created', 'session': new_session.model_dump()})
    return new_session

@app.put("/api/sessions/{session_id}", response_model=Session, tags=["Sessions"])
async def update_session(session_id: str, session_update: SessionCreate):
    """Update a session"""
    if session_id not in data_store.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    existing = data_store.sessions[session_id]
    existing.name = session_update.name
    if session_update.metadata:
        existing.metadata.update(session_update.metadata)
    existing.updated_at = datetime.utcnow()
    
    await notify_change('sessions', {'action': 'updated', 'session': existing.model_dump()})
    return existing

@app.delete("/api/sessions/{session_id}", tags=["Sessions"])
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id not in data_store.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    deleted = data_store.sessions.pop(session_id)
    await notify_change('sessions', {'action': 'deleted', 'session_id': session_id})
    return {"message": "Session deleted", "session": deleted.model_dump()}

# ============================================
# API Endpoints - Cron Jobs
# ============================================

@app.get("/api/cron-jobs", response_model=List[CronJob], tags=["Cron Jobs"])
async def get_cron_jobs():
    """Get all cron jobs"""
    return list(data_store.cron_jobs.values())

@app.get("/api/cron-jobs/{job_id}", response_model=CronJob, tags=["Cron Jobs"])
async def get_cron_job(job_id: str):
    """Get a specific cron job"""
    if job_id not in data_store.cron_jobs:
        raise HTTPException(status_code=404, detail="Cron job not found")
    return data_store.cron_jobs[job_id]

@app.post("/api/cron-jobs", response_model=CronJob, tags=["Cron Jobs"])
async def create_cron_job(job: CronJobCreate):
    """Create a new cron job"""
    new_job = CronJob(
        name=job.name,
        schedule=job.schedule,
        command=job.command,
        enabled=job.enabled
    )
    data_store.cron_jobs[new_job.id] = new_job
    await notify_change('cron_jobs', {'action': 'created', 'job': new_job.model_dump()})
    return new_job

@app.put("/api/cron-jobs/{job_id}", response_model=CronJob, tags=["Cron Jobs"])
async def update_cron_job(job_id: str, job_update: CronJobCreate):
    """Update a cron job"""
    if job_id not in data_store.cron_jobs:
        raise HTTPException(status_code=404, detail="Cron job not found")
    
    existing = data_store.cron_jobs[job_id]
    existing.name = job_update.name
    existing.schedule = job_update.schedule
    existing.command = job_update.command
    if job_update.enabled is not None:
        existing.enabled = job_update.enabled
    
    await notify_change('cron_jobs', {'action': 'updated', 'job': existing.model_dump()})
    return existing

@app.delete("/api/cron-jobs/{job_id}", tags=["Cron Jobs"])
async def delete_cron_job(job_id: str):
    """Delete a cron job"""
    if job_id not in data_store.cron_jobs:
        raise HTTPException(status_code=404, detail="Cron job not found")
    
    deleted = data_store.cron_jobs.pop(job_id)
    await notify_change('cron_jobs', {'action': 'deleted', 'job_id': job_id})
    return {"message": "Cron job deleted", "job": deleted.model_dump()}

@app.post("/api/cron-jobs/{job_id}/toggle", response_model=CronJob, tags=["Cron Jobs"])
async def toggle_cron_job(job_id: str):
    """Toggle cron job enabled status"""
    if job_id not in data_store.cron_jobs:
        raise HTTPException(status_code=404, detail="Cron job not found")
    
    job = data_store.cron_jobs[job_id]
    job.enabled = not job.enabled
    await notify_change('cron_jobs', {'action': 'toggled', 'job': job.model_dump()})
    return job

# ============================================
# API Endpoints - Agents
# ============================================

@app.get("/api/agents", response_model=List[Agent], tags=["Agents"])
async def get_agents():
    """Get all agents"""
    return list(data_store.agents.values())

@app.get("/api/agents/{agent_id}", response_model=Agent, tags=["Agents"])
async def get_agent(agent_id: str):
    """Get a specific agent"""
    if agent_id not in data_store.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    return data_store.agents[agent_id]

@app.post("/api/agents", response_model=Agent, tags=["Agents"])
async def create_agent(agent: AgentCreate):
    """Create a new agent"""
    new_agent = Agent(
        name=agent.name,
        type=agent.type,
        capabilities=agent.capabilities or []
    )
    data_store.agents[new_agent.id] = new_agent
    await notify_change('agents', {'action': 'created', 'agent': new_agent.model_dump()})
    return new_agent

@app.put("/api/agents/{agent_id}", response_model=Agent, tags=["Agents"])
async def update_agent(agent_id: str, agent_update: AgentCreate):
    """Update an agent"""
    if agent_id not in data_store.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    existing = data_store.agents[agent_id]
    existing.name = agent_update.name
    existing.type = agent_update.type
    if agent_update.capabilities:
        existing.capabilities = agent_update.capabilities
    
    await notify_change('agents', {'action': 'updated', 'agent': existing.model_dump()})
    return existing

@app.delete("/api/agents/{agent_id}", tags=["Agents"])
async def delete_agent(agent_id: str):
    """Delete an agent"""
    if agent_id not in data_store.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    deleted = data_store.agents.pop(agent_id)
    await notify_change('agents', {'action': 'deleted', 'agent_id': agent_id})
    return {"message": "Agent deleted", "agent": deleted.model_dump()}

@app.post("/api/agents/{agent_id}/heartbeat", response_model=Agent, tags=["Agents"])
async def agent_heartbeat(agent_id: str):
    """Update agent heartbeat"""
    if agent_id not in data_store.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = data_store.agents[agent_id]
    agent.last_heartbeat = datetime.utcnow()
    agent.status = "idle" if agent.status == "offline" else agent.status
    
    await notify_change('agents', {'action': 'heartbeat', 'agent': agent.model_dump()})
    return agent

@app.post("/api/agents/{agent_id}/status", response_model=Agent, tags=["Agents"])
async def update_agent_status(agent_id: str, status: str):
    """Update agent status"""
    if agent_id not in data_store.agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = data_store.agents[agent_id]
    agent.status = status
    
    await notify_change('agents', {'action': 'status_changed', 'agent': agent.model_dump()})
    return agent

# ============================================
# API Endpoints - Projects
# ============================================

@app.get("/api/projects", response_model=List[Project], tags=["Projects"])
async def get_projects():
    """Get all projects"""
    return list(data_store.projects.values())

@app.get("/api/projects/{project_id}", response_model=Project, tags=["Projects"])
async def get_project(project_id: str):
    """Get a specific project"""
    if project_id not in data_store.projects:
        raise HTTPException(status_code=404, detail="Project not found")
    return data_store.projects[project_id]

@app.post("/api/projects", response_model=Project, tags=["Projects"])
async def create_project(project: ProjectCreate):
    """Create a new project"""
    new_project = Project(
        name=project.name,
        description=project.description
    )
    data_store.projects[new_project.id] = new_project
    await notify_change('projects', {'action': 'created', 'project': new_project.model_dump()})
    return new_project

@app.put("/api/projects/{project_id}", response_model=Project, tags=["Projects"])
async def update_project(project_id: str, project_update: ProjectCreate):
    """Update a project"""
    if project_id not in data_store.projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    existing = data_store.projects[project_id]
    existing.name = project_update.name
    if project_update.description is not None:
        existing.description = project_update.description
    existing.updated_at = datetime.utcnow()
    
    await notify_change('projects', {'action': 'updated', 'project': existing.model_dump()})
    return existing

@app.delete("/api/projects/{project_id}", tags=["Projects"])
async def delete_project(project_id: str):
    """Delete a project"""
    if project_id not in data_store.projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    deleted = data_store.projects.pop(project_id)
    await notify_change('projects', {'action': 'deleted', 'project_id': project_id})
    return {"message": "Project deleted", "project": deleted.model_dump()}

@app.post("/api/projects/{project_id}/progress", response_model=Project, tags=["Projects"])
async def update_project_progress(project_id: str, progress: float):
    """Update project progress"""
    if project_id not in data_store.projects:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = data_store.projects[project_id]
    project.progress = max(0.0, min(100.0, progress))
    project.tasks_completed = int(project.tasks_total * project.progress / 100)
    project.updated_at = datetime.utcnow()
    
    await notify_change('projects', {'action': 'progress_updated', 'project': project.model_dump()})
    return project

# ============================================
# API Endpoints - Stats
# ============================================

@app.get("/api/stats", response_model=Stats, tags=["Stats"])
async def get_stats():
    """Get dashboard statistics"""
    return data_store.get_stats()

@app.get("/api/stats/detailed", tags=["Stats"])
async def get_detailed_stats():
    """Get detailed statistics with breakdowns"""
    stats = data_store.get_stats()
    
    return {
        "summary": stats.model_dump(),
        "breakdown": {
            "sessions_by_status": {
                status: sum(1 for s in data_store.sessions.values() if s.status == status)
                for status in set(s.status for s in data_store.sessions.values())
            },
            "agents_by_status": {
                status: sum(1 for a in data_store.agents.values() if a.status == status)
                for status in set(a.status for a in data_store.agents.values())
            },
            "projects_by_status": {
                status: sum(1 for p in data_store.projects.values() if p.status == status)
                for status in set(p.status for p in data_store.projects.values())
            }
        },
        "recent_activity": {
            "total_tasks_completed": sum(a.tasks_completed for a in data_store.agents.values()),
            "cron_jobs_run_today": sum(1 for c in data_store.cron_jobs.values() if c.last_run and c.last_run.date() == datetime.utcnow().date())
        }
    }

# ============================================
# Health Check
# ============================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API info"""
    return {
        "name": "Mission Control Dashboard API",
        "version": "1.0.0",
        "endpoints": {
            "sessions": "/api/sessions",
            "cron_jobs": "/api/cron-jobs",
            "agents": "/api/agents",
            "projects": "/api/projects",
            "stats": "/api/stats"
        },
        "websocket": "ws://localhost:8000/socket.io/",
        "docs": "/docs"
    }

# ============================================
# Main Entry Point
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(socket_app, host="0.0.0.0", port=8000, reload=True)
