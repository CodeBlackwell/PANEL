# Agent Prompts for LLM Crypto Trading System

## Overview

This directory contains specialized AI agent prompts that serve as the implementation team for the trading system defined in the 6 PRDs located in `/PRDs/`.

Each agent is designed to be used with Claude or similar LLMs to guide implementation of specific subsystems.

## Agent Roster

| Agent | File | Focus Area | Primary PRD |
|-------|------|------------|-------------|
| Data Engineer | `01-data-engineer.md` | Real-time data pipelines | PRD 01 |
| Execution Engineer | `02-execution-engineer.md` | Trade execution & risk | PRD 02 |
| Memory Architect | `03-memory-architect.md` | RAG & memory systems | PRD 03 |
| Orchestrator | `04-orchestrator.md` | Multi-agent coordination | PRD 04 |
| Frontend Engineer | `05-frontend-engineer.md` | Dashboard & visualization | PRD 05 |
| ML Engineer | `06-ml-engineer.md` | RLMF training pipeline | PRD 06 |
| System Architect | `07-system-architect.md` | Cross-system integration | All PRDs |
| Security Engineer | `08-security-engineer.md` | Security & compliance | All PRDs |
| DevOps Engineer | `09-devops-engineer.md` | Infrastructure & deployment | All PRDs |

## Usage

### With Claude Code

```bash
# Load an agent context for implementation work
cat agents/01-data-engineer.md | claude -p "Implement the WebSocket price feed handler"
```

### As System Prompts

Each agent file can be used as a system prompt when working on that subsystem:

1. Copy the agent prompt content
2. Set as system context in your LLM interface
3. Begin implementation discussion

### Multi-Agent Workflow

For complex tasks spanning multiple subsystems:

1. **Start with System Architect** - Define integration points
2. **Domain Agents** - Implement individual subsystems
3. **Security Engineer** - Review for vulnerabilities
4. **DevOps Engineer** - Deploy and monitor

## Agent Communication Protocol

When agents need to coordinate:

```
[FROM: Data Engineer]
[TO: Execution Engineer]
[RE: Price feed schema]

The WebSocket price feed publishes to Redis channel `prices:{symbol}` with schema:
{
  "symbol": "BTC/USDT",
  "price": 50000.00,
  "timestamp": "2024-01-15T10:30:00Z",
  "exchange": "binance"
}

Please confirm this meets execution engine requirements.
```

## Directory Structure

```
agents/
├── README.md                    # This file
├── 01-data-engineer.md          # Data pipeline implementation
├── 02-execution-engineer.md     # Trade execution & risk management
├── 03-memory-architect.md       # RAG & memory system design
├── 04-orchestrator.md           # Multi-agent coordination
├── 05-frontend-engineer.md      # Dashboard & visualization
├── 06-ml-engineer.md            # RLMF training pipeline
├── 07-system-architect.md       # Cross-system integration
├── 08-security-engineer.md      # Security & compliance
└── 09-devops-engineer.md        # Infrastructure & deployment
```

## PRD References

All agents should reference the corresponding PRDs in `/PRDs/`:

- **PRD 01**: Real-Time Data Pipeline Architecture
- **PRD 02**: Trade Execution Engine
- **PRD 03**: Layered Memory System
- **PRD 04**: Multi-Agent Trading Orchestrator
- **PRD 05**: Trading Dashboard
- **PRD 06**: RLMF Training Pipeline

## Best Practices

1. **Always reference PRDs** - Agents should cite specific sections when implementing
2. **Define contracts first** - API schemas and data formats before implementation
3. **Test in isolation** - Each subsystem should be testable independently
4. **Document decisions** - Log architectural decisions and trade-offs
5. **Security by default** - All agents should consider security implications

## Contributing

When adding new agents:

1. Follow the standard template structure
2. Reference relevant PRDs
3. Define clear integration points
4. Include code examples where helpful
5. Update this README
