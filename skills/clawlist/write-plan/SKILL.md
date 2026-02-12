---
name: write-plan
description: |
  Use when: After design/brainstorming is complete and before execution. Creating detailed implementation plans with checkpoints.
  Don't use when: Design is unclear (use brainstorming first), simple tasks with obvious steps, or when following an existing plan.
  Outputs: Markdown plan with checkpoints, tasks, verification criteria, time estimates.
---

# Write Plan

## Overview

Transform validated designs into detailed, actionable implementation plans with checkpoints.

## When to Use

**Use when:**
- Design/brainstorming phase is complete
- Before starting implementation
- Breaking down complex work into steps
- Creating checkpoints for verification
- Estimating time and resources

**Don't use when:**
- Design is unclear (use brainstorming first)
- Simple tasks with obvious steps (<5 tasks)
- Following an existing plan
- Emergency fixes that need immediate action
- Exploratory work without clear end state

Every plan includes:
- Bite-sized tasks (2-5 minutes each)
- Checkpoints with verification criteria
- Estimated time for each section
- Execution options at the end

## Plan Structure Template

Use this exact structure for all plans:

```markdown
# [Project Name] - Implementation Plan

**Goal:** One sentence describing success
**Approach:** Brief summary of the chosen approach
**Estimated Total Time:** X minutes
**Created:** YYYY-MM-DD

## Checkpoint 1: [Milestone Name]
**Time:** ~X minutes

- [ ] Task 1: [Description] (~X min)
  - **Action:** [Specific action to take]
  - **Verify:** [How to confirm it's done correctly]
  
- [ ] Task 2: [Description] (~X min)
  - **Action:** [Specific action to take]
  - **Verify:** [How to confirm it's done correctly]

## Checkpoint 2: [Milestone Name]
...

## Verification Criteria
- [ ] All checkpoints complete
- [ ] Quality standards met
- [ ] User approval obtained
- [ ] Documentation updated (if applicable)

## Risk & Blockers
| Risk | Likelihood | Mitigation |
|------|------------|------------|
| [Potential issue] | High/Med/Low | [How to handle] |

## Execution Options
1. **Single-Agent** - Execute sequentially in this session
2. **Parallel Agents** - Dispatch multiple agents for independent tasks
```

## Task Granularity

- **Small:** 2-5 minutes of work
- **Specific:** Clear what "done" means
- **Verifiable:** Can confirm completion
- **Independent:** Doesn't block on other tasks in same checkpoint

## Execution Handoff

After saving the plan, offer execution choice:

**"Plan complete and saved to `memory/plans/<filename>.md`. Two execution options:**

**1. Single-Agent (this session)** - I execute tasks sequentially, review at each checkpoint

**2. Dispatch Multiple Agents (parallel)** - Spawn subagents for independent tasks

**Which approach?"**

**If Single-Agent chosen:**
- Stay in this session
- Execute tasks sequentially
- Report progress at each checkpoint

**If Dispatch Multiple Agents chosen:**
- Use dispatch-multiple-agents skill
- Spawn subagents for parallel work
- Integrate results

## Integration with Other Skills

- After **brainstorming** → Use write-plan
- Before **doing-tasks** → Plan must exist
- With **dispatch-multiple-agents** → For parallel execution
