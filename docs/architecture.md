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

## Phase 06 Update — Reverse proxy topology

At this stage the Compose stack runs as three services:

- `postgres`: stateful database service
- `app`: FastAPI application container
- `nginx`: reverse proxy entrypoint

### Request Flow

Client request flow is now:

- host -> nginx -> app -> postgres

### Exposure Model

The host should access the application through Nginx, not directly through the app container.

Current host exposure rules:

- `nginx` is published to the host
- `app` is internal-only within the Compose network
- `postgres` remains published to the host on `127.0.0.1:5433` for local administrative access

This keeps the topology closer to a real runtime layout without introducing unnecessary complexity.

### Reverse Proxy Path

Nginx proxies requests to the application using the internal Compose service name:

- `app:8000`

The FastAPI application connects to PostgreSQL using:

- `postgres:5432`

This means the internal service-to-service paths are now:

- nginx -> `app:8000`
- app -> `postgres:5432`

### Compose Network Model

All services remain attached to the same user-defined bridge network:

- `opsledger_net`

This enables service discovery by Compose service name and avoids hardcoding host loopback addresses for internal traffic.

### Host Port Publishing at Phase 06

At this phase, the relevant host entry points are:

- Nginx:
  - `127.0.0.1:${NGINX_PORT}`
- PostgreSQL:
  - `127.0.0.1:5433`

The `app` service is intentionally not published directly to the host in this phase.

### Persistence

PostgreSQL continues to store data in the named volume:

- `opsledger_postgres_data`

This preserves state across container recreation unless the volume is explicitly removed.

### Health Model at Phase 06

Health validation now exists at three levels:

- PostgreSQL health:
  - `pg_isready`
- Application health:
  - `/health/live`
- Nginx health:
  - configuration/runtime validation through container healthcheck

Operationally relevant API checks through Nginx remain:

- `/health/live`
- `/health/ready`
- `/version`

### Why This Topology Matters

This is the first phase where the runtime layout looks closer to a real deployment shape:

- public entrypoint at the reverse proxy
- application isolated behind the proxy
- database only indirectly used by the application
- service discovery handled internally by the Compose network

This is still intentionally local-first and simple, but it is much more interview-defensible than exposing the application container directly as the primary user entrypoint.

### Next Architectural Step

Later phases will extend this topology with:

- Jenkins controller
- Jenkins static agent
- pipeline execution
- blue/green deployment logic
- rollback flow
- runbooks and operational recovery procedures