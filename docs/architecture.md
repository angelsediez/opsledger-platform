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

## Phase 05 Update — Local containerized runtime

At this stage the application runs as a two-service Compose stack:

- `postgres`: stateful database service
- `app`: FastAPI application container

### Networking

Both services are attached to the same user-defined bridge network:

- `opsledger_net`

The application reaches PostgreSQL through the service name:

- `postgres:5432`

### Host port publishing

To avoid collision with the already running local PostgreSQL on host port `5432`, the Compose PostgreSQL service is published on:

- `127.0.0.1:5433`

This host port is only for external access from the host.  
Internal service-to-service communication still uses:

- `postgres:5432`

### Persistence

PostgreSQL data is stored in the named volume:

- `opsledger_postgres_data`

### Health model

- PostgreSQL health: `pg_isready`
- Application health: `/health/live`

This is the local production-style baseline before adding Nginx and Jenkins in later phases.
