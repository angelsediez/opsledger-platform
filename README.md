# OpsLedger Platform

Local-first DevOps/SRE lab built on Ubuntu 24.04 with FastAPI, PostgreSQL, Docker Compose, pytest, Alembic, Jenkins, Bash-based blue/green deployment, and rollback.

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
- health checks
- reverse proxying
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

## Key Technical Decisions

- **Python dependency strategy:**
  - `.venv`
  - `requirements.txt`
  - `requirements-dev.txt`

- **PostgreSQL driver:**
  - `psycopg[binary]==3.3.3`

- **Jenkins strategy:**
  - controller + static Docker-capable agent

- **Migration strategy:**
  - backward-compatible migrations for blue/green and rollback

- **Compose PostgreSQL host port:**
  - `5433` on host
  - `5432` inside the Compose network

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
│   └── .dockerignore
├── jenkins/
│   ├── controller/
│   ├── agent/
│   └── plugins.txt
├── scripts/
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

## Run Locally with Docker Compose

1. **Copy the environment file**

   ```bash
   cp .env.example .env
   ```

2. **Validate the rendered Compose configuration**

   ```bash
   docker compose config
   ```

3. **Build and start the stack**

   ```bash
   docker compose up -d --build
   ```

4. **Run database migrations from the app container**

   ```bash
   docker compose exec app alembic upgrade head
   docker compose exec app alembic current
   ```

5. **Validate the running services**

   ```bash
   docker compose ps
   docker compose logs --no-color postgres
   docker compose logs --no-color app
   ```

6. **Validate the API**

   ```bash
   curl -s http://127.0.0.1:8000/health/live | jq
   curl -s http://127.0.0.1:8000/health/ready | jq
   curl -s http://127.0.0.1:8000/version | jq
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

That means:

- host-side access: `127.0.0.1:5433`
- container-to-container access: `postgres:5432`

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

## Migrations

Database schema changes are managed through Alembic.

### Migration Policy

Because the project will later implement blue/green deployment and rollback, migrations must remain compatible across rollout windows.

Practical rules:

- prefer additive changes first
- avoid destructive schema changes in the same release where rollback is expected
- treat rollback as an application rollback first
- document migration caveats in ADRs and runbooks

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

At the current phase, the stack runs as two Compose services:

- `postgres`
- `app`

Later phases will extend this with:

- Nginx reverse proxy
- Jenkins controller
- Jenkins agent
- blue/green deployment logic
- rollback scripts

## Evidence and Validation

The repository stores visual and operational evidence such as:

- environment baseline screenshots
- FastAPI docs screenshots
- PostgreSQL and Alembic validation
- pytest output and coverage
- Compose runtime validation

### Suggested Evidence Locations

- `assets/screenshots/phase-00/`
- `assets/screenshots/phase-01/`
- `assets/screenshots/phase-02/`
- `assets/screenshots/phase-03/`
- `assets/screenshots/phase-04/`
- `assets/screenshots/phase-05/`

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
