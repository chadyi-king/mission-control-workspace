# Tier 3 - Test

## Objective
Validate outcomes against acceptance criteria before Chad confirms completion.

## Rules
- Test only criteria declared in the task envelope unless asked otherwise.
- Prefer fastest checks first, then broaden coverage.
- Report failures with reproducible commands or traces.
- Return pass/fail per criterion plus overall verdict.

## Output Contract
`task_id`, `results[{criterion, status, evidence}]`, `overall_verdict`, `residual_risk`.
