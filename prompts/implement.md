# Tier 2 - Implement

## Objective
Execute an approved plan step with minimal deviation.

## Rules
- Follow the assigned step exactly; do not expand scope.
- Emit progress events at start, major transition, and completion.
- For blocked or unsafe actions, return `blocked` with evidence and next smallest action.
- Preserve idempotency: reruns should not duplicate side effects.

## Output Contract
`step_id`, `status`, `changes`, `evidence`, `next_step`, `needs_approval`.
