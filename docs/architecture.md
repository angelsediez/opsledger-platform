# Architecture

## High-Level Design

OpsLedger Platform is a local-first production-style lab composed of:

- FastAPI application
- PostgreSQL database
- Nginx reverse proxy
- Jenkins controller
- Jenkins static agent
- Bash deployment/rollback scripts

## Deployment Model

The application will be deployed in blue/green style:

- one active color receives traffic
- one inactive color is prepared for the next release
- traffic switch happens only after health validation
- rollback will switch traffic back to the previous healthy color

## Design Principles

- local-first
- simple, reproducible, interview-defensible
- minimal app complexity
- explicit operational documentation

