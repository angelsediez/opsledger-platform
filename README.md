<div align="center">

<img src="assets/logos/opsledger-logo-horizontal.png" width="560" alt="OpsLedger Platform logo" />

# OpsLedger Platform

### Local-first DevOps/SRE homelab for operating a small internal platform with CI/CD, Nginx, blue/green deployment, rollback, and failure simulation

![Status](https://img.shields.io/badge/Status-Validated_Lab-brightgreen?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-Reverse_Proxy-009639?style=for-the-badge&logo=nginx&logoColor=white)
![Jenkins](https://img.shields.io/badge/Jenkins-CI%2FCD-D24939?style=for-the-badge&logo=jenkins&logoColor=white)

</div>

---

## Overview

**OpsLedger Platform** is a production-inspired local DevOps/SRE homelab built around a small internal FastAPI service. The application surface is intentionally minimal, while the delivery, runtime, rollback, and failure-handling workflows are intentionally operationally rich.

The lab is designed to practice and validate how a service behaves when it is operated with real platform engineering concerns:

- database-backed API runtime with FastAPI, PostgreSQL, SQLAlchemy, and Alembic
- Docker Compose service orchestration with healthchecks and named volumes
- Nginx as the public reverse proxy and traffic-switching entrypoint
- Jenkins controller/agent CI/CD with Pipeline as Code
- local blue/green deployment using `app_blue` and `app_green`
- readiness-gated traffic switching
- manual rollback and deploy-failure simulation
- runbooks, troubleshooting guides, screenshots, and validation evidence

> [!IMPORTANT]
> **Lab State:** Complete v1 local baseline.  
> **Final Baseline:** Phase 10 — rollback hardening, deploy-failure simulation, runbooks, troubleshooting, diagrams, and validation evidence.

---

## Table of Contents

- [System Design](#system-design)
- [Technical Stack](#technical-stack)
- [Completed Baseline](#completed-baseline)
- [Quick Start](#quick-start)
- [Blue/Green Operations](#bluegreen-operations)
- [Jenkins CI/CD](#jenkins-cicd)
- [Evidence Gallery](#evidence-gallery)
- [Repository Map](#repository-map)
- [Key Documentation](#key-documentation)
- [Design Decisions](#design-decisions)
- [Boundaries and Non-Goals](#boundaries-and-non-goals)

---

## System Design

### Runtime Architecture

<p align="center">
  <img src="assets/diagrams/runtime-architecture.png" width="100%" alt="OpsLedger Platform runtime architecture" />
</p>

### CI/CD Flow

<p align="center">
  <img src="assets/diagrams/ci-cd-flow.png" width="100%" alt="OpsLedger Platform CI/CD flow" />
</p>

### Blue/Green Deployment Flow

<p align="center">
  <img src="assets/diagrams/blue-green-deployment.png" width="100%" alt="OpsLedger Platform blue green deployment flow" />
</p>

### Failure and Rollback Flow

<p align="center">
  <img src="assets/diagrams/failure-and-rollback-flow.png" width="100%" alt="OpsLedger Platform failure and rollback flow" />
</p>

---

## Architecture at a Glance

```text
Application runtime

host -> nginx -> app_blue | app_green -> postgres
```

```text
CI/CD runtime

jenkins-controller -> jenkins-agent -> host-mounted CI workspace -> Docker Compose / pytest / blue-green scripts
```

| Domain | Components | Purpose |
| :--- | :--- | :--- |
| API runtime | `app_blue`, `app_green` | FastAPI service variants for blue/green switching |
| Data layer | `postgres` | Persistent PostgreSQL database with Alembic migrations |
| Entrypoint | `nginx` | Public reverse proxy and active-color traffic switch |
| CI control plane | `jenkins-controller` | Jenkins orchestration only, configured with `0` executors |
| CI execution | `jenkins-agent` | Docker-capable static agent that runs builds and deployment scripts |
| Operations | `scripts/`, `runbooks/`, `troubleshooting/` | Deployment, rollback, recovery, and incident guidance |

---

## Technical Stack

### Application and Data

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-D71F00?style=flat-square)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-6B7280?style=flat-square)
![pytest](https://img.shields.io/badge/pytest-Testing-0A9EDC?style=flat-square&logo=pytest&logoColor=white)

### Platform and Delivery

![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/Docker_Compose-Orchestration-2496ED?style=flat-square&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-Reverse_Proxy-009639?style=flat-square&logo=nginx&logoColor=white)
![Jenkins](https://img.shields.io/badge/Jenkins-Pipeline-D24939?style=flat-square&logo=jenkins&logoColor=white)
![Bash](https://img.shields.io/badge/Bash-Automation-4EAA25?style=flat-square&logo=gnubash&logoColor=white)

---

## What This Lab Practices and Validates

| Area | Practiced Capability |
| :--- | :--- |
| API operations | Liveness, readiness, version endpoint, and resource endpoint validation |
| Data operations | PostgreSQL persistence, Alembic migrations, and isolated test database workflow |
| Testing | pytest unit/integration tests, coverage output, and JUnit reports |
| Containerization | Dockerfile, Compose services, healthchecks, environment files, and named volumes |
| Reverse proxy | Nginx as public entrypoint with active-color routing |
| CI/CD | Jenkins controller/agent split, Pipeline as Code, artifacts, and test reports |
| Deployment | local blue/green deployment using `app_blue` and `app_green` |
| Release safety | readiness healthcheck required before Nginx traffic switch |
| Recovery | manual rollback, failed deploy simulation, runbooks, and troubleshooting |

---

## Completed Baseline

| Phase | Scope | Status |
| :--- | :--- | :---: |
| Phase 00 | Host baseline and Docker installation validated | ✅ |
| Phase 01 | Repository structure and base documentation | ✅ |
| Phase 02 | Minimal FastAPI app and operational endpoints | ✅ |
| Phase 03 | PostgreSQL, SQLAlchemy, and Alembic integration | ✅ |
| Phase 04 | pytest unit and integration testing baseline | ✅ |
| Phase 05 | Dockerfile and Docker Compose app stack | ✅ |
| Phase 06 | Nginx reverse proxy in front of the API | ✅ |
| Phase 07 | Jenkins controller + static Docker-capable agent | ✅ |
| Phase 08 | Jenkins Pipeline as Code with real CI | ✅ |
| Phase 09 | Local blue/green deployment and Nginx switch | ✅ |
| Phase 10 | Rollback hardening, deploy-failure simulation, runbooks, troubleshooting, and evidence | ✅ |

---

## Quick Start

### 1. Create local environment file

```bash
cp .env.example .env
```

### 2. Ensure host CI root exists

```bash
mkdir -p /home/angelsediez/jenkins-workspaces
```

### 3. Validate Compose rendering

```bash
docker compose config
```

### 4. Start the app runtime

```bash
docker compose up -d --build --remove-orphans postgres app_blue app_green nginx
```

### 5. Apply migrations

```bash
docker compose exec app_blue alembic upgrade head
docker compose exec app_blue alembic current
```

### 6. Validate services

```bash
docker compose ps
docker compose exec nginx nginx -t
```

### 7. Validate API through Nginx

```bash
set -a
source .env
set +a

curl -s "http://127.0.0.1:${NGINX_PORT}/health/live" | jq
curl -s "http://127.0.0.1:${NGINX_PORT}/health/ready" | jq
curl -s "http://127.0.0.1:${NGINX_PORT}/version" | jq
```

---

## Blue/Green Operations

### Check active color

```bash
./scripts/get-active-color.sh
```

### Validate both colors

```bash
./scripts/healthcheck.sh blue
./scripts/healthcheck.sh green
```

### Deploy inactive color and switch traffic

```bash
./scripts/deploy-blue-green.sh
```

### Validate active color header using GET

```bash
set -a
source .env
set +a

ACTIVE_COLOR="$(./scripts/get-active-color.sh)"
HEADER_COLOR="$(curl -fsS -D - -o /dev/null "http://127.0.0.1:${NGINX_PORT}/health/live" \
  | tr -d '\r' \
  | awk -F': ' '/^X-OpsLedger-Active-Color:/{print $2}')"

echo "Active color file: ${ACTIVE_COLOR}"
echo "Nginx header color: ${HEADER_COLOR}"
test "${HEADER_COLOR}" = "${ACTIVE_COLOR}"
```

### Simulate a controlled failed deploy

```bash
SIMULATE_FAILURE=true ./scripts/deploy-blue-green.sh || true
```

Expected behavior:

- inactive color fails readiness validation
- Nginx traffic switch is aborted
- previous active color remains serving traffic
- failure evidence is stored under `validation/`

### Manual rollback

```bash
./scripts/rollback.sh
```

or explicitly:

```bash
./scripts/rollback.sh blue
./scripts/rollback.sh green
```

---

## Jenkins CI/CD

Jenkins runs with a controller/agent split:

- `jenkins-controller`: orchestration only, configured with `0` executors
- `jenkins-agent`: Docker-capable execution node

The pipeline is defined in:

```text
Jenkinsfile
```

Current pipeline responsibilities:

- checkout from SCM into a host-mounted CI workspace
- validate agent tools
- prepare CI `.env`
- validate Docker Compose config
- create Python virtual environment
- recreate PostgreSQL test database
- run pytest with coverage and JUnit output
- archive test artifacts
- optionally run local blue/green deploy when `RUN_DEPLOY=true`

### Validate last Jenkins build

```bash
set -a
source .env
set +a

curl -s -u "${JENKINS_ADMIN_ID}:${JENKINS_ADMIN_PASSWORD}" \
  "http://127.0.0.1:${JENKINS_HTTP_PORT}/job/opsledger-ci/lastBuild/api/json" \
  | jq '{number,result,building,duration,fullDisplayName}'
```

---

## Evidence Gallery

### API and Testing Baseline

| FastAPI docs | pytest and coverage |
| :---: | :---: |
| <img src="assets/screenshots/phase-02/P02-01-fastapi-docs.png" width="100%" alt="FastAPI docs screenshot" /> | <img src="assets/screenshots/phase-04/P04-01-pytest-collect-and-pass.png" width="100%" alt="pytest passing screenshot" /> |

### Compose and Nginx Runtime

| Compose services | Nginx config and health |
| :---: | :---: |
| <img src="assets/screenshots/phase-05/P05-01-compose-services-up.png" width="100%" alt="Docker Compose services running" /> | <img src="assets/screenshots/phase-06/P06-02-nginx-config-and-health.png" width="100%" alt="Nginx config and health validation" /> |

### Jenkins CI/CD

| Jenkins pipeline success | Test results and artifacts |
| :---: | :---: |
| <img src="assets/screenshots/phase-08/P08-02-jenkins-pipeline-success.png" width="100%" alt="Jenkins pipeline success" /> | <img src="assets/screenshots/phase-08/P08-03-jenkins-test-results-and-artifacts.png" width="100%" alt="Jenkins test results and artifacts" /> |

### Blue/Green Deployment and Rollback

| Blue/green services | Jenkins blue/green deploy |
| :---: | :---: |
| <img src="assets/screenshots/phase-09/P09-01-blue-green-services-running.png" width="100%" alt="blue and green app services running" /> | <img src="assets/screenshots/phase-09/P09-04-jenkins-blue-green-deploy-success.png" width="100%" alt="Jenkins blue green deploy success" /> |

### Failure Simulation and Recovery

| Failed deploy keeps previous color | Manual rollback validation |
| :---: | :---: |
| <img src="assets/screenshots/phase-10/P10-01-failed-deploy-keeps-previous-color-part-3.png" width="100%" alt="failed deploy keeps previous color" /> | <img src="assets/screenshots/phase-10/P10-04-manual-rollback-runbook-validation-part-2.png" width="100%" alt="manual rollback validation" /> |

<details>
<summary><strong>Screenshot inventory</strong></summary>

Evidence is organized by phase under:

```text
assets/screenshots/
├── phase-00/
├── phase-01/
├── phase-02/
├── phase-03/
├── phase-04/
├── phase-05/
├── phase-06/
├── phase-07/
├── phase-08/
├── phase-09/
└── phase-10/
```

</details>

---

## Repository Map

```text
.
├── app/                    # FastAPI app, routers, models, schemas, db wiring
├── alembic/                # Alembic migration environment and versions
├── docker/                 # App Dockerfile and Nginx config
├── jenkins/                # Jenkins controller, agent, plugins, init scripts
├── scripts/                # Blue/green deploy, switch, healthcheck, rollback
├── tests/                  # Unit and integration tests
├── docs/                   # Architecture, setup guide, CI/CD, ADR index
├── runbooks/               # Operational rollback and deploy-failure runbooks
├── troubleshooting/        # Debugging guides for Nginx, Jenkins, Postgres, common errors
├── assets/
│   ├── diagrams/           # Architecture and workflow diagrams
│   ├── logos/              # OpsLedger branding assets
│   └── screenshots/        # Phase-based visual evidence
├── validation/             # Test results, healthcheck logs, validation artifacts
├── docker-compose.yml
├── Jenkinsfile
├── Makefile
├── requirements.txt
└── requirements-dev.txt
```

---

## Key Documentation

| Document | Purpose |
| :--- | :--- |
| [`docs/setup-guide.md`](docs/setup-guide.md) | Full local setup, validation, and operation guide |
| [`docs/architecture.md`](docs/architecture.md) | Architecture evolution and final runtime model |
| [`docs/ci-cd-pipeline.md`](docs/ci-cd-pipeline.md) | Jenkins pipeline model and operational boundaries |
| [`docs/decisions.md`](docs/decisions.md) | ADR index |
| [`runbooks/runbook-rollback.md`](runbooks/runbook-rollback.md) | Manual rollback procedure |
| [`runbooks/runbook-incident-deploy-failure.md`](runbooks/runbook-incident-deploy-failure.md) | Deploy-failure incident response |
| [`troubleshooting/nginx-502.md`](troubleshooting/nginx-502.md) | Nginx 502 diagnosis and recovery |
| [`troubleshooting/jenkins-build-fails.md`](troubleshooting/jenkins-build-fails.md) | Jenkins pipeline failure diagnosis |
| [`troubleshooting/common-errors.md`](troubleshooting/common-errors.md) | Common operational errors |

---

## Design Decisions

- The app is intentionally small so the focus stays on DevOps/SRE workflow.
- PostgreSQL uses host port `5433` to avoid local `5432` conflicts.
- Nginx is the only public app entrypoint.
- Blue/green uses two Compose services: `app_blue` and `app_green`.
- Nginx switches traffic by updating `active_proxy_pass.conf`.
- Readiness healthcheck is mandatory before Nginx traffic switch.
- Rollback is manual, explicit, and traffic-based.
- Jenkins controller does not run builds.
- Jenkins agent mounts Docker socket as a local-lab tradeoff, not a production security pattern.
- CI deployment runs from a host-mounted workspace because Docker bind mounts are resolved by the host daemon.

---

## Boundaries and Non-Goals

This is intentionally a **local-first practice homelab**, not a production deployment platform.

Out of scope for v1:

- Kubernetes rollout logic
- cloud deployment
- registry promotion workflow
- canary routing
- weighted traffic shifting
- service mesh
- Terraform infrastructure provisioning
- Prometheus/Grafana observability stack

These are better as future experiments, separate repositories, or a v2, not required work for this baseline.

---

## Lab Status

> [!IMPORTANT]
> **Status:** Complete ✅  
> **Scope:** Phase 00 through Phase 10 complete.  
> **Lab State:** Completed DevOps/SRE homelab baseline with CI/CD, blue/green deployment, rollback, failure simulation, runbooks, troubleshooting, diagrams, screenshots, and validation evidence.

---

## Author

**Angel Diez**
