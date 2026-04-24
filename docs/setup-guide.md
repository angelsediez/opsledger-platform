# Setup Guide

## Purpose

This guide documents how to prepare, run, validate, and test the OpsLedger Platform local environment.

It is written as an operational setup document, not just as a development note. The goal is to make the stack reproducible on a clean Ubuntu host with minimal ambiguity.

## Scope Covered So Far

This document currently covers:

- host baseline reference
- required local tooling
- Python local environment
- PostgreSQL development container
- FastAPI local execution
- Alembic migrations
- pytest execution
- Docker Compose runtime
- Nginx reverse proxy
- Jenkins local controller and static agent
- Jenkins Pipeline as Code CI baseline
- local blue/green deployment
- manual rollback path

Later phases will extend this document with:

- stronger rollback procedures
- runbooks and recovery guidance

## Host Baseline

Phase 00 was validated on a clean Ubuntu host with the following baseline:

- Ubuntu 24.04.4 LTS
- Kernel 6.17.0-22-generic
- AMD Ryzen Threadripper 1950X
- 32 GiB RAM
- Docker Engine validated locally

## Tooling Installed

Base tooling validated during environment preparation:

- git
- python3
- pip
- make
- jq
- tree
- Docker Engine
- Docker Compose plugin

## Notes from Initial Host Preparation

- Docker repository was successfully configured using the modern keyring/source-file approach
- Docker group refresh was validated with `newgrp docker`
- Docker was fully validated with `docker run --rm hello-world`

## Repository Preparation

Clone the repository or place it under your local projects directory, then move into the project root.

Expected working directory example:

- `~/projects/opsledger-platform`

## Python Environment

The project uses a deliberately simple Python dependency strategy:

- `.venv`
- `requirements.txt`
- `requirements-dev.txt`

### Create the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

### Python Dependency Notes

The PostgreSQL driver for this environment must remain:

- psycopg[binary]==3.3.3

Do not replace it with:

- psycopg==3.3.3

This environment already showed issues with the non-binary variant.

### Environment Variables

The project uses .env.example as the reference configuration.

Create your local runtime file with:

```bash
cp .env.example .env
```

Key configuration values

The most important variables at the current phase are:

- APP_NAME
- APP_ENV
- APP_VERSION
- APP_PORT
- NGINX_PORT
- POSTGRES_DB
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_PORT
- DATABASE_URL
- JENKINS_HTTP_PORT
- JENKINS_ADMIN_ID
- JENKINS_ADMIN_PASSWORD
- JENKINS_AGENT_NAME
- JENKINS_AGENT_SECRET
- HOST_CI_ROOT

### Required host CI root

For Phase 09, define this in both .env.example and .env:

```bash
HOST_CI_ROOT=/home/angelsediez/jenkins-workspaces
```

Create it on the host:

```bash
mkdir -p /home/angelsediez/jenkins-workspaces
```

### Important Port Note

This project intentionally publishes the Compose PostgreSQL service to the host on:

- 127.0.0.1:5433

This avoids conflict with any PostgreSQL already using host port 5432.

Inside the Compose network, the application still connects to PostgreSQL using:

- postgres:5432

That means:

- host-side PostgreSQL access: 127.0.0.1:5433
- container-to-container PostgreSQL access: postgres:5432

At Phase 06+, the application is accessed from the host through Nginx on:

- 127.0.0.1:${NGINX_PORT}

At Phase 07+, Jenkins is accessed from the host on:

- 127.0.0.1:${JENKINS_HTTP_PORT}

### Local Development Database (Pre-Compose Workflow)

Before the Compose stack was introduced, development PostgreSQL was validated using a standalone container. This remains useful for debugging and for understanding the local data flow.

- Create the development volume

```bash
docker volume create opsledger_postgres_dev
```

- Start the development PostgreSQL container

```bash
docker run -d \
--name opsledger-postgres-dev \
-e POSTGRES_DB=opsledger \
-e POSTGRES_USER=opsledger \
-e POSTGRES_PASSWORD=change-me \
-p 5432:5432 \
-v opsledger_postgres_dev:/var/lib/postgresql/data \
postgres:17
```

- Wait until PostgreSQL is ready

```bash
until docker exec opsledger-postgres-dev pg_isready -U opsledger -d opsledger >/dev/null 2>&1; do
sleep 1
done
```

- Validate readiness

```bash
docker exec opsledger-postgres-dev pg_isready -U opsledger -d opsledger
```

### FastAPI Minimal Local Run

This remains useful for local debugging outside Compose.

### Local application startup

```bash
source .venv/bin/activate
export DATABASE_URL="postgresql+psycopg://opsledger:change-me@127.0.0.1:5432/opsledger"
uvicorn app.main:app --reload
```

### Local endpoints introduced by the app

Operational endpoints:

- /health/live
- /health/ready
- /version

Resource endpoints:

- /services
- /deployments
- /incidents

### Validate local endpoints

```bash
curl -s http://127.0.0.1:8000/health/live | jq
curl -s http://127.0.0.1:8000/health/ready | jq
curl -s http://127.0.0.1:8000/version | jq
curl -s http://127.0.0.1:8000/services | jq
curl -s http://127.0.0.1:8000/deployments | jq
curl -s http://127.0.0.1:8000/incidents | jq
```

### Alembic Migrations

Schema changes are managed in-repo using Alembic.

### Migration Environment

Alembic is configured with:

- alembic.ini
- alembic/env.py
- alembic/versions/

### Run migrations locally

```bash
source .venv/bin/activate
export DATABASE_URL="postgresql+psycopg://opsledger:change-me@127.0.0.1:5432/opsledger"
alembic upgrade head
```

### Check current migration revision

```bash
alembic current
```

### Generate a new migration

```bash
alembic revision --autogenerate -m "describe the change here"
```

### Migration Policy

Because the project now supports blue/green deployment and rollback, migration design must remain conservative.

Required rules:

- prefer additive schema changes first
- avoid destructive schema changes in the same release where rollback is expected
- treat rollback as an application rollback first
- document migration caveats in ADRs and runbooks

This matters because in a blue/green window, old and new application versions may briefly coexist against the same database.

### Test Database

Automated tests use a dedicated PostgreSQL database:

- opsledger_test

This keeps test execution separate from the main development database.

### Create the test database

```bash
docker exec opsledger-postgres-dev psql -U opsledger -d postgres -c "DROP DATABASE IF EXISTS opsledger_test WITH (FORCE);"
docker exec opsledger-postgres-dev psql -U opsledger -d postgres -c "CREATE DATABASE opsledger_test;"
```

### Validate that the test database exists

```bash
docker exec opsledger-postgres-dev psql -U opsledger -d postgres -c "\l opsledger_test"
```

### Automated Tests with pytest

The project uses pytest as the main test framework.

### Current testing model

- tests/unit/ for fast unit tests
- tests/integration/ for DB-backed API tests
- shared fixtures in tests/conftest.py

### Run the tests

```bash
source .venv/bin/activate
export TEST_DATABASE_URL="postgresql+psycopg://opsledger:change-me@127.0.0.1:5432/opsledger_test"
pytest --cov=app --cov-report=term-missing tests
```

### Generate HTML coverage

```bash
source .venv/bin/activate
export TEST_DATABASE_URL="postgresql+psycopg://opsledger:change-me@127.0.0.1:5432/opsledger_test"
pytest --cov=app --cov-report=html:validation/test-results/phase-04/htmlcov tests
```

### Validate collected tests before execution

```bash
source .venv/bin/activate
pytest --collect-only
```

### Docker Compose Runtime (Current Recommended Run Path)

As of Phase 09, the preferred local runtime is Docker Compose with:

- postgres
- app_blue
- app_green
- nginx
- jenkins-controller
- jenkins-agent

### Compose Run Procedure

1. Create the local environment file

```bash
cp .env.example .env
```

2. Confirm HOST_CI_ROOT is present

```bash
grep '^HOST_CI_ROOT=' .env.example
grep '^HOST_CI_ROOT=' .env
```

Expected value:

```bash
HOST_CI_ROOT=/home/angelsediez/jenkins-workspaces
```

3. Ensure the host CI workspace root exists

```bash
mkdir -p /home/angelsediez/jenkins-workspaces
```

4. Validate the rendered Compose configuration

```bash
docker compose config
```

5. Verify that ${NGINX_PORT} is free on the host

```bash
set -a
source .env
set +a

ss -ltnp | grep ":${NGINX_PORT}\b" || true
```

Expected result:

- if nothing is shown, the port is free
- if a process is already listening there, stop it or change NGINX_PORT in .env

6. Safely replace the old app stack without leaving orphans

```bash
docker compose down --remove-orphans || true
docker compose up -d --build --remove-orphans postgres app_blue app_green nginx
```

7. Check running services

```bash
docker compose ps
```

### Compose Health and Logs

```bash
docker compose logs --no-color postgres
docker compose logs --no-color app_blue
docker compose logs --no-color app_green
docker compose logs --no-color nginx

docker inspect --format='{{json .State.Health}}' $(docker compose ps -q postgres)
docker inspect --format='{{json .State.Health}}' $(docker compose ps -q app_blue)
docker inspect --format='{{json .State.Health}}' $(docker compose ps -q app_green)
docker inspect --format='{{json .State.Health}}' $(docker compose ps -q nginx)
```

### Run Migrations Inside Compose

After the stack is up, apply migrations from app_blue.

```bash
docker compose exec app_blue alembic upgrade head
docker compose exec app_blue alembic current
docker compose exec postgres psql -U opsledger -d opsledger -c "\dt"
```

### Nginx Validation

```bash
docker compose exec nginx nginx -t
docker compose exec nginx sh -c 'tail -n 20 /var/log/nginx/access.log'
docker compose exec nginx sh -c 'tail -n 20 /var/log/nginx/error.log'
```

### Validate the Running API Through Nginx

At this phase, the host should access the API through Nginx, not directly through the app containers.

### Health endpoints through Nginx

```bash
set -a
source .env
set +a

curl -s http://127.0.0.1:${NGINX_PORT}/health/live | jq
curl -s http://127.0.0.1:${NGINX_PORT}/health/ready | jq
curl -s http://127.0.0.1:${NGINX_PORT}/version | jq
```

### Phase 09 — Local Blue/Green Deployment

### Runtime model

At this phase the application runtime includes:

- app_blue
- app_green
- nginx
- postgres

Only one color receives traffic at a time. The previous color remains available for immediate rollback.

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

### Validate public traffic after the switch

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

or explicitly:

```bash
./scripts/rollback.sh blue
./scripts/rollback.sh green
```

### Jenkins Local-Lab

At Phase 07, Jenkins was added as a local control plane for CI/CD work.

The Jenkins runtime model is:

- jenkins-controller
- jenkins-agent

Important execution rule:

The Jenkins controller is for orchestration only.

The Jenkins agent is where builds should run.

### Check that the Jenkins host port is free

```bash
set -a
source .env
set +a

ss -ltnp | grep ":${JENKINS_HTTP_PORT}\b" || true
```

Expected result:

- if nothing is shown, the port is free
- if a process is already listening there, stop it or change JENKINS_HTTP_PORT in .env
### Start only the controller first

```bash
docker compose up -d --build jenkins-controller
```

### Wait for Jenkins to finish initializing

```bash
set -a
source .env
set +a

until curl -fsS http://127.0.0.1:${JENKINS_HTTP_PORT}/login >/dev/null 2>&1; do
echo "Waiting for Jenkins controller to finish initializing..."
sleep 5
done
```

### Validate controller startup

```bash
docker compose ps
docker compose logs --no-color jenkins-controller | tail -n 100
curl -I http://127.0.0.1:${JENKINS_HTTP_PORT}/login
```

### Log in to Jenkins

Open:

- http://127.0.0.1:${JENKINS_HTTP_PORT}

Use the credentials from .env:

- JENKINS_ADMIN_ID
- JENKINS_ADMIN_PASSWORD

### Create the static agent in the Jenkins UI

Go to:

- Manage Jenkins
- Nodes
- New Node

Use these values:

- Node name: docker-agent
- Type: Permanent Agent
- Remote root directory: /home/jenkins/agent
- Labels: docker linux local
- Number of executors: 2
- Usage: Only build jobs with label expressions matching this node
- Launch method: Launch agent by connecting it to the controller

After saving the node, open the node page and copy the inbound agent secret.

### Ensure Jenkins variables exist in .env.example and .env

Run this block:

```bash
for file in .env.example .env; do
grep -q '^JENKINS_ADMIN_ID=' "$file" || echo 'JENKINS_ADMIN_ID=admin' >> "$file"
grep -q '^JENKINS_ADMIN_PASSWORD=' "$file" || echo 'JENKINS_ADMIN_PASSWORD=change-me-jenkins' >> "$file"
grep -q '^JENKINS_AGENT_NAME=' "$file" || echo 'JENKINS_AGENT_NAME=docker-agent' >> "$file"
grep -q '^JENKINS_AGENT_SECRET=' "$file" || echo 'JENKINS_AGENT_SECRET=' >> "$file"
grep -q '^HOST_CI_ROOT=' "$file" || echo 'HOST_CI_ROOT=/home/angelsediez/jenkins-workspaces' >> "$file"
done
```

### Set the agent secret in .env

Replace PASTE_SECRET_HERE with the real secret copied from Jenkins:

```bash
sed -i 's|^JENKINS_AGENT_SECRET=.*|JENKINS_AGENT_SECRET=PASTE_SECRET_HERE|' .env
```

### Ensure the Jenkins agent mounts the host CI root

The jenkins-agent service must include:

```yaml
environment:
  HOST_CI_ROOT: ${HOST_CI_ROOT}

volumes:
  - /var/run/docker.sock:/var/run/docker.sock
  - ${HOST_CI_ROOT}:${HOST_CI_ROOT}
  - jenkins_agent_workdir:/home/jenkins/agent
```

### Recreate the Jenkins agent

```bash
docker compose --profile jenkins-agent up -d --build jenkins-agent
```

### Validate the agent connection

```bash
set -a
source .env
set +a

docker compose logs --no-color jenkins-agent | tail -n 50

curl -s -u "${JENKINS_ADMIN_ID}:${JENKINS_ADMIN_PASSWORD}" \
"http://127.0.0.1:${JENKINS_HTTP_PORT}/computer/${JENKINS_AGENT_NAME}/api/json" \
| jq '{displayName,offline,temporarilyOffline,assignedLabels}'
```

### Validate installed plugins

```bash
docker compose exec jenkins-controller ls /var/jenkins_home/plugins | egrep 'workflow-aggregator|pipeline-stage-view|git|credentials|matrix-auth|docker-workflow|pipeline-utility-steps|junit|timestamper'
```

### Validate agent tools

```bash
docker compose exec jenkins-agent sh -c 'docker --version && docker compose version && git --version && python3 --version && make --version | head -n 1 && jq --version'
```

### Jenkins Pipeline as Code

### Pipeline goal

At this phase Jenkins executes a real CI pipeline from the repository Jenkinsfile and can continue into local blue/green deployment.

### Jenkins job type

Create a Jenkins job of type:

- Pipeline

Use:

- Pipeline script from SCM

### Job configuration

In Jenkins UI:

- Click New Item
- Name it: opsledger-ci
- Choose: Pipeline

In the job configuration:

- Definition: Pipeline script from SCM
- SCM: Git
- Repository URL: repository URL for this project
- Branch Specifier: */main
- Script Path: Jenkinsfile

### Repository URL note

if git remote get-url origin returns an SSH URL and Jenkins does not have SSH credentials configured, use the HTTPS URL of the public repository in the job configuration if the repository is private, configure the proper Jenkins credentials and use the correct repository URL accordingly

### Important pipeline correction

The Jenkins pipeline does not write these Jenkins variables into the CI .env:

- JENKINS_HTTP_PORT
- JENKINS_ADMIN_ID
- JENKINS_ADMIN_PASSWORD
- JENKINS_AGENT_NAME
- JENKINS_AGENT_SECRET

That avoids repeating the previous failure around JENKINS_AGENT_SECRET.

### Rebuild the Jenkins controller if plugins were changed

If you updated jenkins/plugins.txt, rebuild the controller:

```bash
docker compose up -d --build jenkins-controller
```

Wait until the login page is reachable again before proceeding:

```bash
set -a
source .env
set +a

until curl -fsS "http://127.0.0.1:${JENKINS_HTTP_PORT}/login" >/dev/null 2>&1; do
echo "Waiting for Jenkins controller to finish initializing..."
sleep 5
done
```

### Trigger a build manually from Jenkins UI

Open the job and click:

- Build Now

### Build parameters

The pipeline includes:

- RUN_DEPLOY

Behavior:

- `RUN_DEPLOY=false` → CI only
- `RUN_DEPLOY=true` → CI + local blue/green deployment

### Trigger a build from the API

First get the Jenkins crumb:

```bash
set -a
source .env
set +a

CRUMB=$(curl -s -u "${JENKINS_ADMIN_ID}:${JENKINS_ADMIN_PASSWORD}" \
"http://127.0.0.1:${JENKINS_HTTP_PORT}/crumbIssuer/api/json" \
| jq -r '.crumbRequestField + ":" + .crumb')
```

Then trigger the build:

```bash
curl -s -X POST \
-u "${JENKINS_ADMIN_ID}:${JENKINS_ADMIN_PASSWORD}" \
-H "${CRUMB}" \
"http://127.0.0.1:${JENKINS_HTTP_PORT}/job/opsledger-ci/build"
```

### Validate the last build status

```bash
curl -s -u "${JENKINS_ADMIN_ID}:${JENKINS_ADMIN_PASSWORD}" \
"http://127.0.0.1:${JENKINS_HTTP_PORT}/job/opsledger-ci/lastBuild/api/json" \
| jq '{number,result,building,duration,timestamp}'
```

### Wait for the build to finish

```bash
set -a
source .env
set +a

until [ "$(curl -s -u "${JENKINS_ADMIN_ID}:${JENKINS_ADMIN_PASSWORD}" \
"http://127.0.0.1:${JENKINS_HTTP_PORT}/job/opsledger-ci/lastBuild/api/json" \
| jq -r '.building')" = "false" ]; do
echo "Waiting for Jenkins build to finish..."
sleep 5
done
```

### Validate final build result

```bash
curl -s -u "${JENKINS_ADMIN_ID}:${JENKINS_ADMIN_PASSWORD}" \
"http://127.0.0.1:${JENKINS_HTTP_PORT}/job/opsledger-ci/lastBuild/api/json" \
| jq '{number,result,duration,fullDisplayName}'
```

### Validate console output

```bash
curl -s -u "${JENKINS_ADMIN_ID}:${JENKINS_ADMIN_PASSWORD}" \
"http://127.0.0.1:${JENKINS_HTTP_PORT}/job/opsledger-ci/lastBuild/consoleText" \
| tail -n 120
```

### Validate JUnit results exist

```bash
curl -s -u "${JENKINS_ADMIN_ID}:${JENKINS_ADMIN_PASSWORD}" \
"http://127.0.0.1:${JENKINS_HTTP_PORT}/job/opsledger-ci/lastBuild/testReport/api/json" \
| jq '{failCount,skipCount,totalCount}'
```

### What Should Be True After Validation

You should be able to confirm all of the following.

#### App stack

- `docker compose ps` shows `postgres`, `app_blue`, `app_green`, and `nginx` up
- PostgreSQL is healthy
- both colors are runnable
- Nginx is healthy
- Alembic migrations apply successfully from `app_blue`
- Nginx configuration validates successfully with `nginx -t`
- `/health/live` returns OK through Nginx
- `/health/ready` returns OK through Nginx with database reachable
- blue/green switching works through Nginx
- the previous color remains available for rollback

#### Jenkins stack

- `jenkins-controller` is up
- `http://127.0.0.1:${JENKINS_HTTP_PORT}/login` is reachable
- controller plugins are installed
- controller is used for orchestration, not builds
- `jenkins-agent` connects successfully
- the Jenkins node API shows `"offline": false`
- Docker and required CLI tools are available on the agent
- the `opsledger-ci` pipeline exists
- the pipeline runs from SCM using `Jenkinsfile`
- the pipeline executes on the agent
- `pytest` passes from Jenkins
- blue/green deploy can run from Jenkins when `RUN_DEPLOY=true`
- test artifacts are archived

### Persistence Model

The Compose runtime stores PostgreSQL data in the named volume:

- opsledger_postgres_data

This means the database state should survive container recreation unless you intentionally remove the volume.

Jenkins controller state is stored in:

- jenkins_home

Jenkins agent workdir is stored in:

- jenkins_agent_workdir

### If you want to destroy the Compose database state

```bash
docker compose down -v
```

Use that only when you intentionally want to reset all Compose-managed PostgreSQL data and Jenkins state.

### Stop the Stack

- Stop and remove containers, keep volumes

```bash
docker compose down
```

- Stop and remove containers and volumes

```bash
docker compose down -v
```

### Common Setup Notes

### App-to-DB connection path

Inside Compose, the application must always use:

- postgres:5432

Do not change this to:

- 127.0.0.1:5432
- 127.0.0.1:5433

For the containerized app, container-to-container communication must happen through the Compose service name.

### Nginx-to-app connection path

Inside Compose, Nginx must proxy to one of these backends:

- app_blue:8000
- app_green:8000

### Jenkins controller URL inside Compose

The agent must connect to the controller using:

- http://jenkins-controller:8080/

### Host-side DB access

If you need to connect from the host to the Compose PostgreSQL service, use:

- host: 127.0.0.1
- port: 5433

### Host-side app access

At Phase 06+, the API should be accessed from the host through Nginx:

- host: 127.0.0.1
- port: ${NGINX_PORT}

### Host-side Jenkins access

At Phase 07+, Jenkins should be accessed from the host through:

- host: 127.0.0.1
- port: ${JENKINS_HTTP_PORT}

### Docker socket tradeoff

The Docker socket is mounted only on the Jenkins agent:

- /var/run/docker.sock

This is accepted only as a local-lab tradeoff and should not be treated as a production-grade isolation model.

### Host CI workspace requirement

Because Docker bind mounts are interpreted by the host daemon, Jenkins deployment steps must run from a host-mounted workspace:

- /home/angelsediez/jenkins-workspaces

Without that, bind mounts like the Nginx config files would fail during Jenkins-driven deploys.

### Evidence Expectations

By the current phase, useful validation evidence includes:

- Compose services up
- PostgreSQL health healthy
- blue and green services healthy
- Nginx health healthy
- Alembic migration applied
- Nginx config validated
- active color header visible through Nginx
- blue/green switch succeeded
- manual rollback succeeded
- Jenkins controller up
- Jenkins agent connected
- Jenkins plugin baseline installed
- agent tooling available
- Jenkins pipeline run succeeded
- JUnit test results visible in Jenkins
- archived build artifacts visible in Jenkins
- blue/green healthcheck logs archived

### Related Documents

For broader design and decision context, see:

- README.md
- docs/architecture.md
- docs/ci-cd-pipeline.md
- docs/decisions.md
- docs/adr/

Operational extensions will later be added through:

- runbooks/
- troubleshooting/