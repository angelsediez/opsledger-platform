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

## Phase 07 Update — Local Jenkins control plane

At this stage the local environment also includes a Jenkins control plane composed of:

- `jenkins-controller`
- `jenkins-agent`

This is intentionally a local-lab design: clean enough to explain in interviews, but not over-engineered.

### Jenkins Execution Model

The Jenkins runtime follows a controller/agent split:

- controller: orchestration only
- agent: build execution

The controller is configured with:

- `0` executors

This is intentional. The controller should not be used as the main execution node for builds. Build execution is delegated to the static agent.

### Jenkins Connectivity Model

The static agent connects inbound to the controller using:

- WebSocket inbound mode

This keeps the local topology simpler because it avoids exposing the classic Jenkins TCP agent port externally.

### Jenkins Tooling Model

The Jenkins agent is Docker-capable and is prepared to run future CI tasks with tools such as:

- Docker CLI
- Docker Compose plugin
- git
- python3
- make
- jq

This makes the agent a practical execution node for the pipeline work that begins in later phases.

### Docker Socket Tradeoff

The Jenkins agent mounts the host Docker socket:

- `/var/run/docker.sock`

This is accepted only as a local-lab tradeoff.

It is useful here because it allows the agent to build images and operate the local Docker environment without introducing a more complex build runner design.

However, this must be understood clearly:

- this is not production-grade isolation
- this is not a hardened multi-tenant CI design
- this is an intentional local-lab shortcut for practicality

### Jenkins Network Placement

Both Jenkins services remain attached to the same Compose network:

- `opsledger_net`

This allows the agent to reach the controller internally by service name.

The internal controller URL used by the agent is:

- `http://jenkins-controller:8080/`

### Host Exposure at Phase 07

At this phase, the relevant host-facing entry points become:

- Nginx:
  - `127.0.0.1:${NGINX_PORT}`
- PostgreSQL:
  - `127.0.0.1:5433`
- Jenkins controller:
  - `127.0.0.1:${JENKINS_HTTP_PORT}`

The Jenkins agent is not exposed to the host as a public service entrypoint.

### Persistence at Phase 07

Persistence now exists in three main places:

- PostgreSQL data:
  - `opsledger_postgres_data`
- Jenkins controller state:
  - `jenkins_home`
- Jenkins agent work directory:
  - `jenkins_agent_workdir`

This keeps Jenkins state persistent across container recreation while preserving the existing database persistence model.

### Health and Runtime State at Phase 07

Operational runtime checks now exist across both the application stack and the CI control plane:

#### Application stack
- PostgreSQL health:
  - `pg_isready`
- app health:
  - `/health/live`
- Nginx health:
  - configuration/runtime validation through container healthcheck

#### Jenkins stack
- Jenkins controller health:
  - login endpoint reachable
- Jenkins agent state:
  - online and connected to controller

### Why This Phase Matters

This phase matters architecturally because it introduces a real CI control plane without yet introducing the complexity of:

- pipeline stages
- deployment orchestration
- blue/green switch logic
- rollback automation

In other words:

- the application runtime is now fronted by Nginx
- the CI runtime now exists as controller + agent
- both are local-first
- both are versioned inside the repository
- both are simple enough to operate and explain

That makes the project significantly more defensible in interviews than a setup that only exposes an app container without a proxy or a CI control plane.

### Current Runtime Summary After Phase 07

At this point, the local architecture contains two coordinated domains:

#### Application runtime
- host -> nginx -> app -> postgres

#### CI runtime
- host -> jenkins-controller -> jenkins-agent -> host docker socket

These domains remain separate enough to reason about clearly, while still living inside the same local-lab environment.

### Next Architectural Step

Later phases will extend this architecture with:

- Jenkins Pipeline-as-Code execution
- CI stages driven from the repository Jenkinsfile
- blue/green deployment logic
- rollback flow
- runbooks and operational recovery procedures