# OpsLedger Platform

Local-first operations platform for tracking services, deployments, and incidents, built on Ubuntu 24.04 with FastAPI, PostgreSQL, Nginx, Docker Compose, pytest, Alembic, Jenkins, blue/green deployment, and rollback.

## Goals

- Build a production-style local stack
- Keep the balance at 75% DevOps / 25% application
- Demonstrate CI/CD, reverse proxying, persistence, health checks, blue/green, rollback, and operational documentation

## MVP Scope

- services
- deployments
- incidents
- /health/live
- /health/ready
- /version

## Planned Stack

- FastAPI
- PostgreSQL
- Nginx
- Docker Engine + Docker Compose
- pytest
- Alembic
- Jenkins
- Bash scripts

## Current Status

- Phase 00 completed: host baseline and Docker installation validated
- Phase 01 completed: repository structure and documentation baseline
- Phase 02 completed: minimal FastAPI app scaffold and operational endpoints

## Key Technical Decisions

- Python dependency strategy: .venv + requirements.txt + requirements-dev.txt
- Jenkins strategy: controller + static Docker-capable agent
- Migration strategy: backward-compatible migrations for blue/green and rollback

## Documentation

- docs/setup-guide.md
- docs/architecture.md
- docs/ci-cd-pipeline.md
- docs/decisions.md
- docs/adr/

## Evidence

- assets/screenshots/
- validation/


## Phase 02 Notes

- Minimal FastAPI application scaffold added
- Operational endpoints available:
  - /health/live
  - /health/ready
  - /version
- Stub resource endpoints available:
  - /services
  - /deployments
  - /incidents
- Database-backed readiness will be implemented in Phase 03


## Phase 03 Notes

- PostgreSQL integration added through SQLAlchemy and Alembic
- API resources now persist data in PostgreSQL
- /health/ready now performs a real database reachability check
- Migrations are managed with Alembic from the repository

