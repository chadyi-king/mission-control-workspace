from datetime import datetime, timezone

from fastapi.testclient import TestClient

from helios.service import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert "status" in body
    assert "agents_count" in body
    assert "last_audit" in body


def test_agents_endpoint() -> None:
    response = client.get("/api/agents")
    assert response.status_code == 200
    agents = response.json()
    assert isinstance(agents, list)
    assert all("agent" in item for item in agents)


def test_event_ingest_and_idempotency() -> None:
    payload = {
        "agent": "quanta",
        "ts": datetime.now(timezone.utc).isoformat(),
        "event_type": "signal_detected",
        "payload": {"symbol": "XAU_USD"},
        "status": "success",
        "idempotency_key": "evt-001",
        "model_tier": "mid",
        "model_id": "kimi-2.5",
        "reasoning_summary": "signal parsed",
        "confidence": 0.8,
    }

    first = client.post("/api/events", json=payload)
    assert first.status_code == 200
    assert first.json()["accepted"] is True

    second = client.post("/api/events", json=payload)
    assert second.status_code == 200
    assert second.json()["accepted"] is False


def test_block_protected_file_modification() -> None:
    payload = {
        "agent": "forger",
        "ts": datetime.now(timezone.utc).isoformat(),
        "event_type": "file_change_request",
        "payload": {"action": "modify", "target_file": "AGENTS.md"},
        "status": "partial",
        "idempotency_key": "evt-002",
        "model_tier": "cheap",
        "model_id": "ollama-qwen",
        "reasoning_summary": "attempted governance edit",
        "confidence": 0.2,
    }

    response = client.post("/api/events", json=payload)
    assert response.status_code == 403


def test_sync_endpoint_shape() -> None:
    response = client.get("/api/sync")
    assert response.status_code == 200
    body = response.json()
    assert "agents" in body
    assert "recent_events" in body
    assert "metrics" in body


def test_dashboard_websocket_receives_updates() -> None:
    with client.websocket_connect("/ws/dashboard") as socket:
        first = socket.receive_json()
        assert first["type"] == "snapshot"

        heartbeat_payload = {
            "agent": "chad",
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        heartbeat_response = client.post("/api/heartbeat", json=heartbeat_payload)
        assert heartbeat_response.status_code == 200

        update = socket.receive_json()
        assert update["type"] == "heartbeat"
