# ADR-0001: Jenkins controller + static Docker-capable agent

## Status
Accepted

## Context
This project needs Jenkins running locally in Docker while keeping the setup understandable and interview-defensible.

## Decision
Use:
- one Jenkins controller container
- one static Jenkins agent container
- builds executed on the agent, not on the controller
- Docker CLI available on the agent
- host Docker socket mounted on the agent as a local-lab tradeoff

## Consequences
### Positive
- cleaner separation of coordination and execution
- stronger interview narrative
- closer to real CI architecture than controller-only

### Negative
- more setup than controller-only
- Docker socket access remains a security tradeoff and must be documented as local-lab only

