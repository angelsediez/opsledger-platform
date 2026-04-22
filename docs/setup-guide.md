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
