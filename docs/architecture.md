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

## Phase 08 Update — CI execution enters the repository

At this phase the Jenkins runtime stops being only infrastructure and starts executing a real CI pipeline from the repository itself.

### Pipeline Execution Model

- the pipeline definition lives in `Jenkinsfile`
- Jenkins loads the pipeline from SCM
- the pipeline is executed on the static agent
- the controller remains orchestration-only

This means the CI behavior is now versioned with the repository instead of living only in Jenkins UI configuration.

### Execution Path

Current CI execution path is:

- Jenkins controller -> Jenkins agent -> repository workspace -> Docker Compose / pytest

The agent is now the actual execution surface for repository validation.

### Current CI Responsibilities

The current pipeline handles:

- source checkout
- environment validation
- CI-local `.env` preparation
- Docker Compose configuration validation
- Python virtual environment preparation
- PostgreSQL test database preparation
- pytest execution
- JUnit result publication
- artifact archiving

This is the first phase where Jenkins is no longer just “present” in the stack, but actually performs useful CI work against the repository.

### Pipeline Boundary at Phase 08

What is implemented now:

- SCM-backed Pipeline as Code
- execution on the labeled static agent
- repository validation
- test database recreation for CI
- pytest-based CI verification
- JUnit and artifact publication

What is still intentionally deferred:

- deployment stages
- image promotion flow
- blue/green switch logic
- rollback automation

This keeps the CI design clean and interview-defensible without jumping too early into deployment complexity.

### Why Phase 08 Matters Architecturally

Phase 08 is important because the project now has:

- a fronted application runtime
- a persistent database runtime
- a Jenkins controller/agent split
- a real repository-driven CI path

That combination moves the project from “infra prepared for CI” to “infra actively validating the repo.”

This is a significant jump in credibility because the repository now contains not only the application code and operational docs, but also the executable CI behavior.

### Current Runtime Summary After Phase 08

At this point, the local architecture contains two active coordinated domains:

#### Application runtime

- host -> nginx -> app -> postgres

#### CI runtime

- host -> jenkins-controller -> jenkins-agent -> repository workspace -> Docker Compose / pytest

The CI runtime now consumes the same repository that defines the application and operational stack.

## Phase 09 Update — Local blue/green switching enters the runtime

At this phase the application runtime evolves from a single internal app service to two explicit color variants:

- `app_blue`
- `app_green`

### Blue/Green Execution Model

Only one color is active behind Nginx at a time.

The public request flow becomes:

- host -> nginx -> active color -> postgres

The inactive color is deployed first, validated, and only then promoted to receive traffic.

### Switch Mechanism

Nginx remains the public entrypoint and now owns the traffic switch through a small included config fragment.

The switch flow is:

- determine the current active color
- identify the inactive color
- deploy or recreate the inactive color
- validate `/health/ready` on the inactive color
- rewrite the active Nginx include
- validate Nginx configuration
- reload Nginx
- keep the previous color running for immediate rollback

This keeps the switching logic understandable and interview-defensible without introducing orchestration complexity beyond what the project needs.

### Nginx Routing Model at Phase 09

Nginx now defines upstreams for both colors:

- `app_blue_backend`
- `app_green_backend`

Traffic selection is controlled by the included file:

- `docker/nginx/conf.d/includes/active_proxy_pass.conf`

The initial state points to blue:

- `proxy_pass http://app_blue_backend;`
- `add_header X-OpsLedger-Active-Color blue always;`

This also gives a simple external validation signal through the response header.

### Runtime Services at Phase 09

The application domain now includes:

- `postgres`
- `app_blue`
- `app_green`
- `nginx`

The CI domain remains:

- `jenkins-controller`
- `jenkins-agent`

### Health Model at Phase 09

Health validation now matters at two levels:

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

This is the promotion gate for the blue/green flow.

### Rollback Model at Phase 09

Rollback is intentionally simple and traffic-based.

The previous color remains running after the switch.  
Rollback consists of:

- validating the other color
- updating the active Nginx include
- reloading Nginx

This provides an immediate return path without first rebuilding the previous color.

### Shared Database Constraint

Both colors share the same PostgreSQL database.

That keeps the local-lab model simple and efficient, but it introduces an important operational constraint:

- schema changes must remain backward-compatible across a switch and rollback window

This is why the migration policy remains conservative.

### Jenkins + Bind Mount Constraint

At Phase 09, Jenkins can execute the blue/green deployment flow.

Because the Jenkins agent uses the host Docker socket, Compose bind mounts are interpreted by the host daemon, not by the agent container filesystem.

That means the deployment pipeline must run from a host-mounted workspace path that exists on the host itself.

For this reason the project uses:

- `HOST_CI_ROOT=/home/angelsediez/jenkins-workspaces`

and the Jenkins agent mounts:

- `${HOST_CI_ROOT}:${HOST_CI_ROOT}`

The pipeline checks out into:

- `${HOST_CI_ROOT}/opsledger-ci-workspace`

Without that correction, relative bind mounts such as the Nginx config files would fail during Jenkins-driven deploys.

### Jenkins Role at Phase 09

The Jenkins controller remains orchestration-only.

The Jenkins agent remains the execution surface for:

- checkout
- test execution
- Compose validation
- blue/green deployment
- traffic switch verification

No deployment work is moved onto the controller.

### Current Runtime Summary After Phase 09

At this point, the local architecture contains two coordinated domains:

#### Application runtime

- host -> nginx -> app_blue|app_green -> postgres

#### CI runtime

- host -> jenkins-controller -> jenkins-agent -> host-mounted CI workspace -> Docker Compose / pytest / blue-green scripts

### Why Phase 09 Matters Architecturally

Phase 09 is the point where the project moves from CI-only validation into controlled runtime switching.

The repository now contains:

- application code
- infra code
- reverse-proxy switch logic
- CI code
- deployment scripts
- manual rollback path

That makes the project substantially stronger as a DevOps/SRE portfolio artifact because it now demonstrates not only build and test automation, but also operational release control and rollback thinking.

### Limitations of This Phase

This is intentionally a local-lab blue/green model, not an enterprise-grade deployment platform.

It does not include:

- canary rollout
- weighted routing
- registry promotion workflow
- service mesh
- Kubernetes rollout logic
- multi-environment release management

Those are intentionally deferred so the design remains focused, executable, and defendable.

### Next Architectural Step

Later phases will extend this architecture with:

- stronger rollback procedure
- explicit runbooks
- failure handling around deployment steps
- operational recovery documentation