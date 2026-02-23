# agentic-mission-control (Helios)

Helios is the mission-control orchestration API between Caleb, Chad, Cerebronn, and execution agents.

## Implemented API
- `GET /api/health`
- `GET /api/agents`
- `POST /api/events`
- `POST /api/heartbeat`
- `POST /api/replay`
- `GET /api/sync`
- `WS /ws/dashboard`

## Quickstart
```bash
cd /home/chad-yi/mission-control-workspace
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
uvicorn helios.service:app --host 0.0.0.0 --port 8000 --reload
```

## Docker Compose startup
```bash
cd /home/chad-yi/mission-control-workspace
docker compose up --build -d
docker compose logs -f helios
```

## User flow
Caleb -> Chad -> Cerebronn -> Helios -> Agents -> Helios -> Chad -> Caleb

## Notes
- `agents/quanta-v3` is intentionally untouched.
