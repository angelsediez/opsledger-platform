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
- Phase 01 in progress: repository structure and documentation baseline

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

