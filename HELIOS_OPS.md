# HELIOS_OPS.md

## Roles
- Caleb: owner and sole approver for high-risk actions.
- Chad: face and user-facing communication layer.
- Cerebronn: brain and planner.
- Helios: spine and orchestrator.

## Approval Policy
- High-risk actions require Caleb approval:
  - Financial execution (live trades, withdrawals, irreversible transactions)
  - Governance updates affecting `AGENTS.md` or `SOUL.md`
  - Destructive operations (mass deletes, service shutdowns)
- Routine non-financial actions can proceed without Caleb approval.

## Safety Defaults
- Trade systems default to `DRY_RUN=true`.
- Programmatic requests that attempt to modify `AGENTS.md` or `SOUL.md` are blocked.
- Idempotency is mandatory for all agent events.

## Runtime Controls
- Replay endpoint requires `x-helios-replay-token`.
- All events must include model provenance and confidence fields.

## Audit Requirements
- Log every approval decision with timestamp and actor.
- Keep event audit records for replay/debug workflows.
