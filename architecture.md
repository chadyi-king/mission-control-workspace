# Helios Architecture

## Role topology
- Caleb initiates mission intent from dashboard.
- Chad validates intent and operational constraints.
- Cerebronn structures execution plan.
- Helios orchestrates ingest, status, replay, and dashboard sync.
- Agents execute scoped work and report outcomes back to Helios.

## Event contract
- `POST /api/events` accepts structured event envelopes (`agent`, `event_type`, `status`, `payload`, optional `idempotency_key`, timestamps).
- `POST /api/heartbeat` updates per-agent liveness.
- `GET /api/sync` returns dashboard snapshot (`agents`, `recent_events`, `metrics`, `last_audit`).
- `GET /api/agents` and `GET /api/health` provide read-side status.

## Idempotency / guardrails
- Idempotency is enforced via event keys in the store to prevent duplicate event ingestion.
- Protected governance file modifications (`AGENTS.md`, `SOUL.md`) are blocked at API level for write-like actions.
- Replay is token-gated through `POST /api/replay` with `HELIOS_REPLAY_TOKEN`.

## Realtime dashboard
- `WS /ws/dashboard` sends an initial snapshot on connect.
- Heartbeats and event ingest operations are broadcast in realtime to connected dashboard clients.

## Storage / queue now and next
- Current state is in-memory (`InMemoryStore`) for queueing, metrics, event history, and agent status.
- Optional adapters already support external wiring: Redis stream path for queue/event fanout and Postgres persistence for durable audit/state.
- Weaviate is available through adapter configuration for semantic memory integration.

## Deployment phases
- Phase 1 (current): in-memory Helios API with websocket dashboard feed and replay controls.
- Phase 2: enable Redis stream-backed queue/event transport via adapters.
- Phase 3: enable Postgres persistence for durable mission/audit lifecycle.
- Phase 4: expand Weaviate-backed retrieval and policy intelligence.
