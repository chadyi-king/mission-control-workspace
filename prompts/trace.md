# Tier 3 - Trace

## Objective
Reconstruct event history for incidents, regressions, or unclear agent behavior.

## Rules
- Build timeline from Helios events, approvals, and agent outputs.
- Identify first bad transition, impacted components, and confidence level.
- Separate facts from assumptions.
- Recommend the smallest safe corrective action.

## Output Contract
`incident_id`, `timeline[]`, `root_cause_hypotheses[]`, `confirmed_findings[]`, `recommended_fix`, `follow_up_checks[]`.
