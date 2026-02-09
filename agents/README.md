# Agent Configuration Directory

This directory contains agent-specific configurations and skills.

## Agents to be Spawned

### A-Series (Core)
- [ ] escritor - Story Agent
- [ ] autour - Script Agent  
- [ ] clair - Streaming Scout
- [ ] quanta - Trading Dev
- [ ] helios - Mission Control Engineer
- [ ] e++ - Core Coding Specialist

### B-Series (Operations)
- [ ] kotler - Marketing Ops
- [ ] ledger - CRM & Docs

### C-Series (Research)
- [ ] atlas - Callings Research

### Utility
- [ ] pulsar - Reminder + Data Sentinel
- [ ] mensamusa - Trading Agent
- [ ] abed - Community Manager

## Status: PENDING SYSTEM SUPPORT

The OpenClaw instance currently only supports the "main" agent.
Multi-agent spawning requires system configuration changes.

## Workaround: Skill-Based Agents

Until multi-agent spawning is available, agents can be simulated via:
1. **Skill files** in `/skills/` directory
2. **Task-specific prompts** with agent personas
3. **Cron jobs** for scheduled agent tasks
