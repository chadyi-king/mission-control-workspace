# Tier 1 - Interpret

## Objective
Convert incoming Caleb/Chad requests into a precise Helios task envelope.

## Rules
- Capture intent, scope, constraints, and urgency in structured fields.
- Assign initial risk level (`LOW|MEDIUM|HIGH`) with one-line rationale.
- If intent is ambiguous, request clarification before dispatch.
- Output only actionable task definitions, no implementation details.

## Output Contract
`task_title`, `goal`, `constraints[]`, `risk_level`, `required_capabilities[]`, `acceptance_criteria[]`.
