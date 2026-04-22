# Setup Guide

## Host Baseline

**Phase 00 validated on:**
- Ubuntu 24.04.4 LTS
- Kernel 6.17.0-22-generic
- AMD Ryzen Threadripper 1950X
- 31 GiB RAM
- Docker Engine validated locally

## Tooling Installed
- git
- python3 / pip
- make
- jq
- tree
- Docker Engine
- Docker Compose plugin

## Notes
- Docker repository was successfully configured using the modern keyring/source-file approach.
- Group refresh was validated with `newgrp docker`.

## Phase 02 — FastAPI Minimal Application

### Python Environment

Create and activate the local environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### Run the API locally

```bash
uvicorn app.main:app --reload
```

### Endpoints introduced in Phase 02
- `/health/live`
- `/health/ready`
- `/version`
- `/services`
- `/deployments`
- `/incidents`

### Notes
- `/health/ready` is still provisional in Phase 02.
- PostgreSQL-backed readiness starts in Phase 03.
- Domain endpoints are still stub responses in this phase.

## Phase 03 — PostgreSQL, SQLAlchemy, and Alembic

### Development database container

Create the PostgreSQL development container:

    docker volume create opsledger_postgres_dev

    docker run -d \
      --name opsledger-postgres-dev \
      -e POSTGRES_DB=opsledger \
      -e POSTGRES_USER=opsledger \
      -e POSTGRES_PASSWORD=change-me \
      -p 5432:5432 \
      -v opsledger_postgres_dev:/var/lib/postgresql/data \
      postgres:17

### Install database dependencies

    source .venv/bin/activate
    pip install -r requirements.txt -r requirements-dev.txt

### Run migrations

    export DATABASE_URL="postgresql+psycopg://opsledger:change-me@127.0.0.1:5432/opsledger"
    alembic upgrade head

### Run the API

    source .venv/bin/activate
    export DATABASE_URL="postgresql+psycopg://opsledger:change-me@127.0.0.1:5432/opsledger"
    uvicorn app.main:app --reload


## Phase 04 — Automated Tests with pytest

### Test database

The test suite uses a dedicated PostgreSQL database:

    opsledger_test

Create it inside the existing PostgreSQL container:

    docker exec opsledger-postgres-dev psql -U opsledger -d postgres -c "DROP DATABASE IF EXISTS opsledger_test WITH (FORCE);"
    docker exec opsledger-postgres-dev psql -U opsledger -d postgres -c "CREATE DATABASE opsledger_test;"

### Run tests

    source .venv/bin/activate
    export TEST_DATABASE_URL="postgresql+psycopg://opsledger:change-me@127.0.0.1:5432/opsledger_test"
    pytest --cov=app --cov-report=term-missing tests

