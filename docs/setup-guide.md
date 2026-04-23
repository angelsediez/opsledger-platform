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
- Docker Compose runtime for:
  - app
  - postgres

Later phases will extend this document with:

- Nginx reverse proxy
- Jenkins controller and agent
- CI pipeline execution
- blue/green deployment
- rollback procedures

## Host Baseline

Phase 00 was validated on a clean Ubuntu host with the following baseline:

- Ubuntu 24.04.4 LTS
- Kernel 6.17.0-22-generic
- AMD Ryzen Threadripper 1950X
- 31 GiB RAM
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

- Docker repository was successfully configured using the modern keyring/source-file approach.
- Docker group refresh was validated with `newgrp docker`.
- Docker was fully validated with `docker run --rm hello-world`.

## Repository Preparation

Clone the repository or place it under your local projects directory, then move into the project root.

Expected working directory example:

`~/projects/opsledger-platform`

## Python Environment

The project uses a deliberately simple Python dependency strategy:

- `.venv`
- `requirements.txt`
- `requirements-dev.txt`

### Create the virtual environment

```bash
python3 -m venv .venv
```

### Activate it

```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### Python Dependency Notes

The PostgreSQL driver for this environment must remain:

```text
psycopg[binary]==3.3.3
```

Do not replace it with:

```text
psycopg==3.3.3
```

This environment already showed issues with the non-binary variant.

## Environment Variables

The project uses `.env.example` as the reference configuration.

Create your local runtime file with:

```bash
cp .env.example .env
```

### Key configuration values

The most important variables at the current phase are:

- `APP_NAME`
- `APP_ENV`
- `APP_VERSION`
- `APP_PORT`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_PORT`
- `DATABASE_URL`

## Important Port Note

This project intentionally publishes the Compose PostgreSQL service to the host on:

```text
127.0.0.1:5433
```

This avoids conflict with any PostgreSQL already using host port `5432`.

Inside the Compose network, the application still connects to PostgreSQL using:

```text
postgres:5432
```

That means:

- host-side access: `127.0.0.1:5433`
- container-to-container access: `postgres:5432`

## Local Development Database (Pre-Compose Workflow)

Before the Compose stack was introduced, development PostgreSQL was validated using a standalone container. This remains useful for debugging and for understanding the local data flow.

### Create the development volume

```bash
docker volume create opsledger_postgres_dev
```

### Start the development PostgreSQL container

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

### Wait until PostgreSQL is ready

```bash
until docker exec opsledger-postgres-dev pg_isready -U opsledger -d opsledger >/dev/null 2>&1; do
  sleep 1
done
```

### Validate readiness

```bash
docker exec opsledger-postgres-dev pg_isready -U opsledger -d opsledger
```

## FastAPI Minimal Local Run

This remains useful for local debugging outside Compose.

### Local application startup

```bash
source .venv/bin/activate
export DATABASE_URL="postgresql+psycopg://opsledger:change-me@127.0.0.1:5432/opsledger"
uvicorn app.main:app --reload
```

### Local endpoints introduced by the app

Operational endpoints:

- `/health/live`
- `/health/ready`
- `/version`

Resource endpoints:

- `/services`
- `/deployments`
- `/incidents`

### Validate local endpoints

```bash
curl -s http://127.0.0.1:8000/health/live | jq
curl -s http://127.0.0.1:8000/health/ready | jq
curl -s http://127.0.0.1:8000/version | jq
curl -s http://127.0.0.1:8000/services | jq
curl -s http://127.0.0.1:8000/deployments | jq
curl -s http://127.0.0.1:8000/incidents | jq
```

## Alembic Migrations

Schema changes are managed in-repo using Alembic.

### Migration environment

Alembic is configured with:

- `alembic.ini`
- `alembic/env.py`
- `alembic/versions/`

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

## Migration Policy

Because the project will later support blue/green deployment and rollback, migration design must remain conservative.

### Required rules

- prefer additive schema changes first
- avoid destructive schema changes in the same release where rollback is expected
- treat rollback as an application rollback first
- document migration caveats in ADRs and runbooks

This matters because in a blue/green window, old and new application versions may briefly coexist against the same database.

## Test Database

Automated tests use a dedicated PostgreSQL database:

```text
opsledger_test
```

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

## Automated Tests with pytest

The project uses pytest as the main test framework.

### Current testing model

- `tests/unit/` for fast unit tests
- `tests/integration/` for DB-backed API tests
- shared fixtures in `tests/conftest.py`

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

## Docker Compose Runtime (Current Recommended Run Path)

As of Phase 05, the preferred local runtime is Docker Compose.

The current stack includes:

- `postgres`
- `app`

## Compose Run Procedure

### 1. Create the local environment file

```bash
cp .env.example .env
```

### 2. Validate the rendered Compose configuration

```bash
docker compose config
```

### 3. Build and start the stack

```bash
docker compose up -d --build
```

### 4. Check running services

```bash
docker compose ps
```

## Compose Health and Logs

### View PostgreSQL logs

```bash
docker compose logs --no-color postgres
```

### View app logs

```bash
docker compose logs --no-color app
```

### Inspect PostgreSQL health status

```bash
docker inspect --format='{{json .State.Health}}' $(docker compose ps -q postgres)
```

### Inspect app health status

```bash
docker inspect --format='{{json .State.Health}}' $(docker compose ps -q app)
```

## Run Migrations Inside Compose

After the stack is up, apply migrations from the app container.

### Apply migrations

```bash
docker compose exec app alembic upgrade head
```

### Check current revision

```bash
docker compose exec app alembic current
```

### Validate database tables from the PostgreSQL container

```bash
docker compose exec postgres psql -U opsledger -d opsledger -c "\dt"
```

## Validate the Running API in Compose

### Health endpoints

```bash
set -a
source .env
set +a

curl -s http://127.0.0.1:${APP_PORT}/health/live | jq
curl -s http://127.0.0.1:${APP_PORT}/health/ready | jq
curl -s http://127.0.0.1:${APP_PORT}/version | jq
```

### CRUD validation

```bash
set -a
source .env
set +a

curl -s -X POST http://127.0.0.1:${APP_PORT}/services \
  -H 'Content-Type: application/json' \
  -d '{"name":"opsledger-api","owner_team":"platform","tier":"internal","description":"Primary API service for OpsLedger."}' | jq

curl -s http://127.0.0.1:${APP_PORT}/services | jq

curl -s -X POST http://127.0.0.1:${APP_PORT}/deployments \
  -H 'Content-Type: application/json' \
  -d '{"service_id":1,"version":"0.1.0","environment":"local","status":"planned"}' | jq

curl -s http://127.0.0.1:${APP_PORT}/deployments | jq

curl -s -X POST http://127.0.0.1:${APP_PORT}/incidents \
  -H 'Content-Type: application/json' \
  -d '{"service_id":1,"severity":"low","status":"open","summary":"Compose validation incident."}' | jq

curl -s http://127.0.0.1:${APP_PORT}/incidents | jq
```

## What Should Be True After Compose Validation

You should be able to confirm all of the following:

- `docker compose ps` shows both services up
- PostgreSQL is healthy
- app is healthy
- Alembic migrations apply successfully from the app container
- `/health/live` returns OK
- `/health/ready` returns OK with database reachable
- service, deployment, and incident records can be created and listed
- PostgreSQL state persists through the named volume

## Persistence Model

The Compose runtime stores PostgreSQL data in the named volume:

```text
opsledger_postgres_data
```

This means the database state should survive container recreation unless you intentionally remove the volume.

### If you want to destroy the Compose database state

```bash
docker compose down -v
```

Use that only when you intentionally want to reset all Compose-managed PostgreSQL data.

## Stop the Stack

### Stop and remove containers, keep volume

```bash
docker compose down
```

### Stop and remove containers and volume

```bash
docker compose down -v
```

## Common Setup Notes

### App-to-DB connection path

Inside Compose, the application must always use:

```text
postgres:5432
```

Do not change this to:

```text
127.0.0.1:5432
```

or

```text
127.0.0.1:5433
```

for the containerized app, because container-to-container communication must happen through the Compose service name.

### Host-side DB access

If you need to connect from the host to the Compose PostgreSQL service, use:

- host: `127.0.0.1`
- port: `5433`

## Evidence Expectations

By the current phase, useful validation evidence includes:

- Compose services up
- PostgreSQL health healthy
- app health healthy
- Alembic migration applied
- `/health/ready` returning success
- CRUD validation against the Compose stack
- pytest outputs and coverage artifacts

## Related Documents

For broader design and decision context, see:

- `README.md`
- `docs/architecture.md`
- `docs/ci-cd-pipeline.md`
- `docs/decisions.md`
- `docs/adr/`

Operational extensions will later be added through:

- `runbooks/`
- `troubleshooting/`