# OpsLedger Platform

Local-first DevOps/SRE lab built on Ubuntu 24.04 with FastAPI, PostgreSQL, Docker Compose, Nginx, pytest, Alembic, Jenkins, Bash-based blue/green deployment, and rollback.

## Purpose

OpsLedger Platform is a production-style local environment designed to demonstrate practical DevOps and SRE workflows around a small but realistic internal API.

The project is intentionally balanced to keep the focus on platform engineering and operations:

- 75% DevOps / SRE
- 25% application code

The application is intentionally small, but the delivery model is not. The goal is to build and operate a reproducible local stack that includes:

- API runtime
- database persistence
- migrations
- automated tests
- containerization
- Compose orchestration
- reverse proxying
- health checks
- CI/CD
- blue/green deployment
- rollback
- operational documentation
- troubleshooting
- evidence and screenshots

## MVP Scope

The MVP application scope is intentionally limited to:

- services
- deployments
- incidents
- `/health/live`
- `/health/ready`
- `/version`

This keeps the domain realistic enough to justify infrastructure and operational workflows without turning the project into an application-heavy build.

## Planned Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- pytest
- Docker Engine
- Docker Compose
- Nginx
- Jenkins
- Bash scripts

## Current Status

Completed so far:

- Phase 00 — host baseline and Docker installation validated
- Phase 01 — repository structure and base documentation created
- Phase 02 — minimal FastAPI app scaffold and operational endpoints added
- Phase 03 — PostgreSQL, SQLAlchemy, and Alembic integration added
- Phase 04 — pytest unit and integration testing baseline added
- Phase 05 — app dockerized and stack runs with Docker Compose
- Phase 06 — Nginx added as reverse proxy in front of the app
- Phase 07 — Jenkins local-lab added with controller + static Docker-capable agent
- Phase 08 — Jenkins Pipeline as Code implemented with a real CI pipeline
- Phase 09 — local blue/green deployment added with Nginx switch and healthcheck

## Key Technical Decisions

- **Python dependency strategy**
  - `.venv`
  - `requirements.txt`
  - `requirements-dev.txt`

- **PostgreSQL driver**
  - `psycopg[binary]==3.3.3`

- **Jenkins strategy**
  - controller + static Docker-capable agent

- **Migration strategy**
  - backward-compatible migrations for blue/green and rollback

- **Compose PostgreSQL host port**
  - `5433` on host
  - `5432` inside the Compose network

- **Reverse proxy strategy**
  - Nginx is the host entrypoint

- **Jenkins execution strategy**
  - controller with `0` executors
  - builds run on the agent, not on the controller

- **Docker socket tradeoff**
  - `/var/run/docker.sock` is mounted only on the Jenkins agent
  - accepted only as a local-lab tradeoff, not as a production-grade isolation model

- **Blue/green strategy**
  - `app_blue` and `app_green` run as separate services
  - Nginx controls active traffic through an include file
  - previous color remains available for immediate rollback

- **Jenkins + bind mount strategy**
  - CI checkout runs from a host-mounted workspace at:
    - `/home/angelsediez/jenkins-workspaces`
  - required because Docker bind mounts are interpreted by the host daemon, not the filesystem inside the Jenkins agent container

## Repository Structure

```text
.
├── app/
│   ├── dependencies/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── db.py
│   ├── main.py
│   └── __init__.py
├── docker/
│   ├── Dockerfile
│   ├── nginx/
│   │   └── conf.d/
│   │       └── includes/
│   └── .dockerignore
├── jenkins/
│   ├── controller/
│   │   └── init.groovy.d/
│   ├── agent/
│   └── plugins.txt
├── scripts/
│   ├── deploy-blue-green.sh
│   ├── get-active-color.sh
│   ├── healthcheck.sh
│   ├── rollback.sh
│   ├── switch-nginx.sh
│   └── utils/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── docs/
│   ├── adr/
│   ├── architecture.md
│   ├── ci-cd-pipeline.md
│   ├── decisions.md
│   └── setup-guide.md
├── runbooks/
├── troubleshooting/
├── assets/
│   ├── diagrams/
│   ├── screenshots/
│   └── logos/
├── validation/
│   ├── test-results/
│   ├── healthcheck-logs/
│   └── load-test-results/
├── alembic/
├── notes/
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── Jenkinsfile
├── LICENSE
├── Makefile
├── pytest.ini
├── README.md
├── requirements.txt
└── requirements-dev.txt
```

## Application Endpoints

### Operational Endpoints

- `GET /health/live`
- `GET /health/ready`
- `GET /version`

### Resource Endpoints

- `GET /services`
- `POST /services`
- `GET /deployments`
- `POST /deployments`
- `GET /incidents`
- `POST /incidents`

## Application Runtime

At Phase 09, the app runtime is:

- `postgres`
- `app_blue`
- `app_green`
- `nginx`

Current public request flow:

```text
host -> nginx -> active color -> postgres
```

Only one color receives public traffic at a time.

## Run Locally with Docker Compose

1. Copy the environment file.

```bash
cp .env.example .env
```

2. Make sure `HOST_CI_ROOT` exists in `.env` and `.env.example`.

```bash
HOST_CI_ROOT=/home/angelsediez/jenkins-workspaces
```

3. Create the host CI workspace root.

```bash
mkdir -p /home/angelsediez/jenkins-workspaces
```

4. Validate the rendered Compose configuration.

```bash
docker compose config
```

5. Check that the Nginx host port is free.

```bash
set -a
source .env
set +a

ss -ltnp | grep ":${NGINX_PORT}\b" || true
```

6. Safely replace the old app stack without leaving orphans.

```bash
docker compose down --remove-orphans || true
docker compose up -d --build --remove-orphans postgres app_blue app_green nginx
```

7. Run database migrations from `app_blue`.

```bash
docker compose exec app_blue alembic upgrade head
docker compose exec app_blue alembic current
```

8. Validate the running services.

```bash
docker compose ps
docker compose logs --no-color postgres
docker compose logs --no-color app_blue
docker compose logs --no-color app_green
docker compose logs --no-color nginx
```

9. Validate the API through Nginx.

```bash
set -a
source .env
set +a

curl -s http://127.0.0.1:${NGINX_PORT}/health/live | jq
curl -s http://127.0.0.1:${NGINX_PORT}/health/ready | jq
curl -s http://127.0.0.1:${NGINX_PORT}/version | jq
```

## Blue/Green Deployment

Phase 09 adds a local blue/green deployment model with:

- `app_blue`
- `app_green`

Nginx switches traffic by changing a small included config file.

### Blue/green scripts

- `scripts/get-active-color.sh`
- `scripts/healthcheck.sh`
- `scripts/switch-nginx.sh`
- `scripts/deploy-blue-green.sh`
- `scripts/rollback.sh`

### Check current active color

```bash
./scripts/get-active-color.sh
```

### Validate both colors independently

```bash
./scripts/healthcheck.sh blue
./scripts/healthcheck.sh green
```

### Deploy inactive color and switch traffic

```bash
./scripts/deploy-blue-green.sh
```

### Validate switched traffic

```bash
set -a
source .env
set +a

curl -sI http://127.0.0.1:${NGINX_PORT}/health/live | grep -i X-OpsLedger-Active-Color
curl -s  http://127.0.0.1:${NGINX_PORT}/health/ready | jq
curl -s  http://127.0.0.1:${NGINX_PORT}/version | jq
```

### Manual rollback

```bash
./scripts/rollback.sh
```

Or explicitly:

```bash
./scripts/rollback.sh blue
./scripts/rollback.sh green
```

## Jenkins Local-Lab

Phase 07 added a separate Jenkins control plane to the same local environment:

- `jenkins-controller`
- `jenkins-agent`

Phase 08 turned that runtime into a real CI baseline using `Jenkinsfile`.

Phase 09 extends that pipeline to run local blue/green deployment when requested.

### Jenkins runtime goals

- keep the setup simple and interview-defensible
- separate controller and agent
- keep builds off the controller
- execute CI/CD through Pipeline as Code from the repo

### Initial Jenkins runtime validation

1. Check that the Jenkins host port is free.

```bash
set -a
source .env
set +a

ss -ltnp | grep ":${JENKINS_HTTP_PORT}\b" || true
```

2. Start only the controller first.

```bash
docker compose up -d --build jenkins-controller
```

3. Wait for Jenkins to finish initializing.

```bash
set -a
source .env
set +a

until curl -fsS http://127.0.0.1:${JENKINS_HTTP_PORT}/login >/dev/null 2>&1; do
  echo "Waiting for Jenkins controller to finish initializing..."
  sleep 5
done
```

4. Log in to Jenkins.

Open:

```text
http://127.0.0.1:${JENKINS_HTTP_PORT}
```

Use credentials from `.env`:

- `JENKINS_ADMIN_ID`
- `JENKINS_ADMIN_PASSWORD`

5. Create the static agent in the Jenkins UI.

Use these values:

- Node name: `docker-agent`
- Type: `Permanent Agent`
- Remote root directory: `/home/jenkins/agent`
- Labels: `docker linux local`
- Number of executors: `2`
- Usage: `Only build jobs with label expressions matching this node`
- Launch method: `Launch agent by connecting it to the controller`

6. Set the agent secret in `.env`.

After Jenkins shows the inbound agent secret, set:

```bash
JENKINS_AGENT_SECRET=<copied-secret>
```

7. Make sure the Jenkins agent mounts the host CI root.

The `jenkins-agent` service must include:

```yaml
environment:
  HOST_CI_ROOT: ${HOST_CI_ROOT}

volumes:
  - /var/run/docker.sock:/var/run/docker.sock
  - ${HOST_CI_ROOT}:${HOST_CI_ROOT}
  - jenkins_agent_workdir:/home/jenkins/agent
```

8. Start the agent.

```bash
docker compose --profile jenkins-agent up -d --build jenkins-agent
```

9. Validate the agent connection.

```bash
set -a
source .env
set +a

curl -s -u "${JENKINS_ADMIN_ID}:${JENKINS_ADMIN_PASSWORD}" \
  "http://127.0.0.1:${JENKINS_HTTP_PORT}/computer/${JENKINS_AGENT_NAME}/api/json" \
  | jq '{displayName,offline,temporarilyOffline,assignedLabels}'
```

10. Validate installed plugins.

```bash
docker compose exec jenkins-controller ls /var/jenkins_home/plugins | egrep 'workflow-aggregator|pipeline-stage-view|git|credentials|matrix-auth|docker-workflow|pipeline-utility-steps|junit|timestamper'
```

11. Validate agent tools.

```bash
docker compose exec jenkins-agent sh -c 'docker --version && docker compose version && git --version && python3 --version && make --version | head -n 1 && jq --version'
```

## Jenkins Pipeline CI/CD

### What the current pipeline does

- checkout from SCM into:
  - `/home/angelsediez/jenkins-workspaces/opsledger-ci-workspace`
- validate tools and runtime environment on the agent
- prepare a CI-local `.env`
- validate Docker Compose configuration
- prepare Python virtual environment
- recreate the PostgreSQL test database
- run pytest with coverage
- publish JUnit results
- archive test output and coverage artifacts
- optionally deploy inactive color and switch traffic through Nginx

### Important CI correction

The Jenkins pipeline does **not** write these Jenkins variables into the CI `.env`:

- `JENKINS_HTTP_PORT`
- `JENKINS_ADMIN_ID`
- `JENKINS_ADMIN_PASSWORD`
- `JENKINS_AGENT_NAME`
- `JENKINS_AGENT_SECRET`

That avoids repeating the previous failure around `JENKINS_AGENT_SECRET`.

### Create the Jenkins job

Create a Jenkins job of type:

```text
Pipeline
```

Use:

```text
Pipeline script from SCM
```

Configuration:

- Definition: `Pipeline script from SCM`
- SCM: `Git`
- Branch Specifier: `*/main`
- Script Path: `Jenkinsfile`

#### Repository URL note

- if `git remote get-url origin` returns an SSH URL and Jenkins does not have SSH credentials configured, use the HTTPS URL of the public repository in the job configuration
- if the repository is private, configure the proper Jenkins credentials and use the correct repository URL accordingly

### Run CI only or CI + deploy

The Jenkins job includes the parameter:

```text
RUN_DEPLOY
```

Behavior:

- `RUN_DEPLOY=false` → CI only
- `RUN_DEPLOY=true` → CI + local blue/green deploy

### Trigger the build from Jenkins UI

Open the job and click:

```text
Build Now
```

### Trigger the build from the Jenkins API

```bash
set -a
source .env
set +a

CRUMB=$(curl -s -u "${JENKINS_ADMIN_ID}:${JENKINS_ADMIN_PASSWORD}" \
  "http://127.0.0.1:${JENKINS_HTTP_PORT}/crumbIssuer/api/json" \
  | jq -r '.crumbRequestField + ":" + .crumb')

curl -s -X POST \
  -u "${JENKINS_ADMIN_ID}:${JENKINS_ADMIN_PASSWORD}" \
  -H "${CRUMB}" \
  "http://127.0.0.1:${JENKINS_HTTP_PORT}/job/opsledger-ci/build"
```

### Validate the last build

```bash
set -a
source .env
set +a

curl -s -u "${JENKINS_ADMIN_ID}:${JENKINS_ADMIN_PASSWORD}" \
  "http://127.0.0.1:${JENKINS_HTTP_PORT}/job/opsledger-ci/lastBuild/api/json" \
  | jq '{number,result,building,duration,timestamp}'
```

### Validate published test results

```bash
set -a
source .env
set +a

curl -s -u "${JENKINS_ADMIN_ID}:${JENKINS_ADMIN_PASSWORD}" \
  "http://127.0.0.1:${JENKINS_HTTP_PORT}/job/opsledger-ci/lastBuild/testReport/api/json" \
  | jq '{failCount,skipCount,totalCount}'
```

## Important Networking Note

This project intentionally publishes the Compose PostgreSQL service on:

```text
127.0.0.1:5433
```

This avoids conflict with any local PostgreSQL already using host port `5432`.

Inside the Compose network, the application still connects to PostgreSQL using the service name:

```text
postgres:5432
```

At the current phase, host traffic reaches the API through Nginx:

```text
127.0.0.1:${NGINX_PORT}
```

Jenkins is exposed separately on:

```text
127.0.0.1:${JENKINS_HTTP_PORT}
```

That means:

- host-side PostgreSQL access: `127.0.0.1:5433`
- container-to-container PostgreSQL access: `postgres:5432`
- host-side application access: `127.0.0.1:${NGINX_PORT}`
- host-side Jenkins access: `127.0.0.1:${JENKINS_HTTP_PORT}`

## Local Development Without Compose

A local `.venv` workflow is also supported for earlier phases and debugging.

### Create and activate the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### Run the app locally

```bash
export DATABASE_URL="postgresql+psycopg://opsledger:change-me@127.0.0.1:5432/opsledger"
uvicorn app.main:app --reload
```

## Automated Testing

The test suite uses pytest with:

- unit tests
- integration tests
- fixtures in `tests/conftest.py`
- coverage output stored under `validation/test-results/`

### Create the test database

```bash
docker exec opsledger-postgres-dev psql -U opsledger -d postgres -c "DROP DATABASE IF EXISTS opsledger_test WITH (FORCE);"
docker exec opsledger-postgres-dev psql -U opsledger -d postgres -c "CREATE DATABASE opsledger_test;"
```

### Run the tests

```bash
source .venv/bin/activate
export TEST_DATABASE_URL="postgresql+psycopg://opsledger:change-me@127.0.0.1:5432/opsledger_test"
pytest --cov=app --cov-report=term-missing tests
```

## Health Model

### `/health/live`

Checks that the API process is responding.

### `/health/ready`

Checks that the API is responding and that PostgreSQL is reachable.

This separation is deliberate because later phases will use these endpoints in:

- Compose healthchecks
- reverse proxy validation
- deployment scripts
- blue/green validation
- rollback logic

## Data Persistence

PostgreSQL data is stored in the named Docker volume:

```text
opsledger_postgres_data
```

This ensures that the Compose stack is reproducible while preserving database state across container restarts.

Jenkins controller state is stored in:

```text
jenkins_home
```

Jenkins agent work directory is stored in:

```text
jenkins_agent_workdir
```

## Migrations

Database schema changes are managed through Alembic.

### Migration Policy

Because the project will later implement blue/green deployment and rollback, migrations must remain compatible across rollout windows.

Practical rules:

- prefer additive changes first
- avoid destructive schema changes in the same release where rollback is expected
- treat rollback as an application rollback first
- document migration caveats in ADRs and runbooks

## Reverse Proxy Validation Through Nginx

At Phase 06+, Nginx is the expected host entrypoint for the app stack.

### Validate Nginx configuration

```bash
docker compose exec nginx nginx -t
```

### Inspect Nginx logs

```bash
docker compose exec nginx sh -c 'tail -n 20 /var/log/nginx/access.log'
docker compose exec nginx sh -c 'tail -n 20 /var/log/nginx/error.log'
```

## Jenkins Plugin Baseline

The current plugin baseline is:

- `workflow-aggregator`
- `pipeline-stage-view`
- `git`
- `credentials`
- `matrix-auth`
- `docker-workflow`
- `pipeline-utility-steps`
- `junit`
- `timestamper`

This plugin set is enough to support the current CI/CD baseline without over-engineering the Jenkins runtime.

## Documentation

Project documentation is part of the deliverable, not an afterthought.

### Primary Docs

- `docs/setup-guide.md`
- `docs/architecture.md`
- `docs/ci-cd-pipeline.md`
- `docs/decisions.md`
- `docs/adr/`

### Operational Docs

- `runbooks/`
- `troubleshooting/`

### Evidence

- `assets/screenshots/`
- `validation/`

## Architecture Summary

At the current phase, the stack runs as:

### Application Runtime

- `postgres`
- `app_blue`
- `app_green`
- `nginx`

### CI Runtime

- `jenkins-controller`
- `jenkins-agent`

Current request flow for the application stack:

```text
host -> nginx -> active color -> postgres
```

Current CI execution model:

```text
jenkins-controller -> jenkins-agent -> host-mounted CI workspace -> Docker Compose / pytest / blue-green scripts
```

Later phases will extend this with:

- stronger rollback flow
- runbooks and operational recovery procedures

## Evidence and Validation

The repository stores visual and operational evidence such as:

- environment baseline screenshots
- FastAPI docs screenshots
- PostgreSQL and Alembic validation
- pytest output and coverage
- Compose runtime validation
- Nginx reverse proxy validation
- Jenkins controller validation
- Jenkins agent connectivity validation
- Jenkins pipeline execution validation
- blue/green deploy validation
- rollback validation

### Suggested Evidence Locations

- `assets/screenshots/phase-00/`
- `assets/screenshots/phase-01/`
- `assets/screenshots/phase-02/`
- `assets/screenshots/phase-03/`
- `assets/screenshots/phase-04/`
- `assets/screenshots/phase-05/`
- `assets/screenshots/phase-06/`
- `assets/screenshots/phase-07/`
- `assets/screenshots/phase-08/`
- `assets/screenshots/phase-09/`

## Roadmap

Planned sequence:

- Phase 00 — Baseline host and tooling
- Phase 01 — Repository structure and documentation baseline
- Phase 02 — Minimal FastAPI app
- Phase 03 — PostgreSQL + SQLAlchemy + Alembic
- Phase 04 — pytest baseline
- Phase 05 — Dockerfile + Compose stack
- Phase 06 — Nginx reverse proxy
- Phase 07 — Jenkins local in Docker
- Phase 08 — Jenkinsfile + CI pipeline
- Phase 09 — Blue/green deployment + switch + healthcheck
- Phase 10 — Rollback + runbooks
- Phase 11 — Final README/docs/evidence polish