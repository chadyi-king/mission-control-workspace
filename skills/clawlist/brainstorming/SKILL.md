---
name: brainstorming
description: |
  Use when: Creative work, new features, building components, adding functionality, modifying existing behavior, or designing systems before implementation.
  Don't use when: Executing known tasks (use doing-tasks), fixing bugs with clear solutions, or following existing plans (use write-plan/doing-tasks).
  Outputs: Validated design decisions, approach selection, clarified requirements.
---

# Brainstorming Ideas Into Designs

## Overview

Help turn ideas into fully formed designs and specs through natural collaborative dialogue.

## When to Use

**Use when:**
- Creating new features or functionality
- Building components or systems
- Adding capabilities to existing code
- Modifying existing behavior
- Designing before implementation
- Exploring multiple approaches

**Don't use when:**
- Executing known tasks (use doing-tasks)
- Following an existing plan (use doing-tasks)
- Fixing bugs with clear, obvious solutions
- Simple configuration changes
- Tasks where the approach is already decided

## The Process

**Understanding the idea:**
- Check out the current project state first (files, docs, recent commits)
- Ask questions one at a time to refine the idea
- Prefer multiple choice questions when possible, but open-ended is fine too
- Only one question per message - if a topic needs more exploration, break it into multiple questions
- Focus on understanding: purpose, constraints, success criteria

**Exploring approaches:**
- Propose 2-3 different approaches with trade-offs
- Present options conversationally with your recommendation and reasoning
- Lead with your recommended option and explain why

**Presenting the design:**
- Once you believe you understand what you're building, present the design
- Break it into sections of 200-300 words
- Ask after each section whether it looks right so far
- Cover: architecture, components, data flow, error handling, testing
- Be ready to go back and clarify if something doesn't make sense

## After Brainstorming

Once design is validated, proceed to **write-plan** skill to create the implementation plan.

## Key Principles

- **One question at a time** - Don't overwhelm with multiple questions
- **Multiple choice preferred** - Easier to answer than open-ended when possible
- **YAGNI ruthlessly** - Remove unnecessary features from all designs
- **Explore alternatives** - Always propose 2-3 approaches before settling
- **Incremental validation** - Present design in sections, validate each
- **Be flexible** - Go back and clarify when something doesn't make sense
