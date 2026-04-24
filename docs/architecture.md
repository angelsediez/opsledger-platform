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

The application uses a local blue/green style:

- one active color receives traffic
- one inactive color is prepared for the next release
- traffic switch happens only after health validation
- rollback switches traffic back to the previous healthy color

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

## Phase 06 Update — Reverse proxy topology

At this stage the Compose stack runs as three services:

- `postgres`
- `app`
- `nginx`

### Request Flow

Client request flow is now:

- host -> nginx -> app -> postgres

### Exposure Model

The host should access the application through Nginx, not directly through the app container.

Current host exposure rules:

- `nginx` is published to the host
- `app` is internal-only within the Compose network
- `postgres` remains published to the host on `127.0.0.1:5433` for local administrative access

### Reverse Proxy Path

Nginx proxies requests to the application using the internal Compose service name:

- `app:8000`

The FastAPI application connects to PostgreSQL using:

- `postgres:5432`

### Compose Network Model

All services remain attached to the same user-defined bridge network:

- `opsledger_net`

### Health Model at Phase 06

Health validation exists at three levels:

- PostgreSQL health:
  - `pg_isready`
- Application health:
  - `/health/live`
- Nginx health:
  - configuration/runtime validation through container healthcheck

## Phase 07 Update — Local Jenkins control plane

At this stage the local environment also includes a Jenkins control plane composed of:

- `jenkins-controller`
- `jenkins-agent`

### Jenkins Execution Model

The Jenkins runtime follows a controller/agent split:

- controller: orchestration only
- agent: build execution

The controller is configured with:

- `0` executors

### Jenkins Connectivity Model

The static agent connects inbound to the controller using:

- WebSocket inbound mode

### Jenkins Tooling Model

The Jenkins agent is Docker-capable and prepared to run CI tasks with tools such as:

- Docker CLI
- Docker Compose plugin
- git
- python3
- make
- jq

### Docker Socket Tradeoff

The Jenkins agent mounts the host Docker socket:

- `/var/run/docker.sock`

This is accepted only as a local-lab tradeoff.

### Jenkins Network Placement

Both Jenkins services remain attached to the same Compose network:

- `opsledger_net`

The internal controller URL used by the agent is:

- `http://jenkins-controller:8080/`

### Host Exposure at Phase 07

The relevant host-facing entry points are:

- Nginx:
  - `127.0.0.1:${NGINX_PORT}`
- PostgreSQL:
  - `127.0.0.1:5433`
- Jenkins controller:
  - `127.0.0.1:${JENKINS_HTTP_PORT}`

### Persistence at Phase 07

Persistence now exists in three main places:

- PostgreSQL data:
  - `opsledger_postgres_data`
- Jenkins controller state:
  - `jenkins_home`
- Jenkins agent work directory:
  - `jenkins_agent_workdir`

## Phase 08 Update — CI execution enters the repository

At this stage the Jenkins runtime stops being only infrastructure and starts executing a real CI pipeline from the repository itself.

### Pipeline Execution Model

- the pipeline definition lives in `Jenkinsfile`
- Jenkins loads the pipeline from SCM
- the pipeline is executed on the static agent
- the controller remains orchestration-only

### Execution Path

Current CI execution path is:

- Jenkins controller -> Jenkins agent -> repository workspace -> Docker Compose / pytest

### Current CI Responsibilities

The CI pipeline handles:

- source checkout
- environment validation
- CI-local `.env` preparation
- Docker Compose configuration validation
- Python virtual environment preparation
- PostgreSQL test database preparation
- pytest execution
- JUnit result publication
- artifact archiving

## Phase 09 Update — Local blue/green switching enters the runtime

At this stage the application runtime evolves from a single internal app service to two explicit color variants:

- `app_blue`
- `app_green`

### Blue/Green Execution Model

Only one color is active behind Nginx at a time.

The public request flow becomes:

- host -> nginx -> active color -> postgres

The inactive color is deployed first, validated, and only then promoted to receive traffic.

### Switch Mechanism

Nginx remains the public entrypoint and owns the traffic switch through a small included config fragment.

The switch flow is:

- determine the current active color
- identify the inactive color
- deploy or recreate the inactive color
- validate `/health/ready` on the inactive color
- rewrite the active Nginx include
- validate Nginx configuration
- reload Nginx
- keep the previous color running for immediate rollback

### Nginx Routing Model

Nginx defines upstreams for both colors:

- `app_blue_backend`
- `app_green_backend`

Traffic selection is controlled by the included file:

- `docker/nginx/conf.d/includes/active_proxy_pass.conf`

The initial state points to blue:

- `proxy_pass http://app_blue_backend;`
- `add_header X-OpsLedger-Active-Color blue always;`

### Runtime Services

The application domain now includes:

- `postgres`
- `app_blue`
- `app_green`
- `nginx`

The CI domain remains:

- `jenkins-controller`
- `jenkins-agent`

### Health Model at Phase 09

Health validation matters at two levels:

#### Container health

- PostgreSQL:
  - `pg_isready`
- `app_blue`:
  - `/health/live`
- `app_green`:
  - `/health/live`
- Nginx:
  - `nginx -t`

#### Deployment promotion health

Before switching traffic, the inactive color must pass:

- `/health/ready`

### Rollback Model at Phase 09

Rollback is intentionally simple and traffic-based.

The previous color remains running after the switch.

Rollback consists of:

- validating the other color
- updating the active Nginx include
- reloading Nginx

### Shared Database Constraint

Both colors share the same PostgreSQL database.

That keeps the local-lab model simple and efficient, but it introduces an important operational constraint:

- schema changes must remain backward-compatible across a switch and rollback window

### Jenkins + Bind Mount Constraint

Because the Jenkins agent uses the host Docker socket, Compose bind mounts are interpreted by the host daemon, not by the agent container filesystem.

For this reason the project uses:

- `HOST_CI_ROOT=/home/angelsediez/jenkins-workspaces`

The Jenkins agent mounts:

- `${HOST_CI_ROOT}:${HOST_CI_ROOT}`

The pipeline checks out into:

- `${HOST_CI_ROOT}/opsledger-ci-workspace`

## Phase 10 Update — Rollback hardening and deploy-failure recovery

At this stage the blue/green model is no longer just able to switch and roll back traffic; it also has hardened manual operating procedures and explicit failure behavior.

### Hardening Goals

Phase 10 adds operational hardening in four areas:

- stricter validation in Bash scripts
- mandatory healthcheck before switch
- controlled deploy-failure simulation
- documented recovery and rollback procedures

### Mandatory Healthcheck Before Switch

The deployment flow now treats readiness as a strict promotion gate.

That means:

- the inactive color must pass `/health/ready`
- Nginx traffic is not switched unless that check passes
- a failed promotion leaves the previous active color serving traffic

This is the most important safety boundary in the current release process.

### Failed Deploy Behavior

A failed deploy of the inactive color does not change public traffic.

The expected behavior is:

- target color fails healthcheck
- switch is aborted
- active Nginx include remains unchanged
- previous active color continues serving requests

This behavior is intentionally conservative and easy to explain in interviews.

### Rollback Remains Manual and Traffic-Based

Rollback is still manual by design.

That means:

- operators validate the target rollback color
- operators switch traffic through Nginx only after validation
- the system does not attempt complex automated rollback orchestration

This keeps the model simple, local-first, and auditable.

### Runbooks and Troubleshooting Now Exist

Operational documentation now exists for:

- manual rollback
- deploy failure on inactive color
- Nginx 502 diagnosis
- Jenkins build failure diagnosis
- common operational errors

This is an important architectural maturity step because the project now includes not only runtime and CI logic, but also explicit recovery guidance.

### Current Runtime Summary After Phase 10

At this point, the local architecture contains two coordinated domains:

#### Application runtime

```text
host -> nginx -> app_blue|app_green -> postgres
```

#### CI runtime

```text
host -> jenkins-controller -> jenkins-agent -> host-mounted CI workspace -> Docker Compose / pytest / blue-green scripts
```

### Why Phase 10 Matters Architecturally

Phase 10 is the point where the project moves from a working release mechanism to a more defensible operational system.

The repository now contains:

- application code
- infra code
- reverse-proxy switch logic
- CI code
- deployment scripts
- rollback hardening
- failure simulation
- runbooks
- troubleshooting guidance

That makes the project stronger as a DevOps/SRE portfolio artifact because it now demonstrates release safety thinking, operational documentation, and recovery discipline.

### Limitations of the Current Model

This is still intentionally a local-lab blue/green model, not an enterprise-grade deployment platform.

It does not include:

- canary rollout
- weighted routing
- registry promotion workflow
- service mesh
- Kubernetes rollout logic
- multi-environment release management

Those are intentionally out of scope to keep the design focused, executable, and defendable.