# CI/CD Pipeline

## Purpose

This document describes the intended CI/CD shape of the OpsLedger Platform project.

At Phase 08, the project now has a functional Jenkins CI pipeline driven by the repository `Jenkinsfile`.

The goal of this document is to define clearly what is implemented now and what is intentionally deferred to later phases.

## Current CI Pipeline

The current Jenkins pipeline is a Declarative Pipeline stored in the repository root as:

- `Jenkinsfile`

The job is configured as:

- `Pipeline`
- `Pipeline script from SCM`
- SCM: `Git`

This keeps the pipeline versioned with the source code and aligned with the Pipeline-as-Code model.

## Current Execution Model

- Jenkins controller coordinates
- Jenkins agent executes
- controller executors remain `0`
- pipeline uses the agent label:
  - `docker && linux && local`

## Job Configuration Note

When configuring the Jenkins job repository URL:

- if `git remote get-url origin` returns an SSH URL and Jenkins does not have SSH credentials configured, use the HTTPS URL of the public repository in the job configuration
- if the repository is private, configure the proper Jenkins credentials and use the correct repository URL accordingly

## Implemented Phase 08 Stages

1. Checkout source
2. Validate tools and runtime environment
3. Prepare CI `.env`
4. Validate Docker Compose configuration
5. Prepare Python virtual environment
6. Prepare PostgreSQL test database
7. Run pytest with coverage and JUnit XML output

## Stage Intent

### Checkout

Performs `checkout scm` from the repository configured in Jenkins.

### Validate Environment

Confirms the Jenkins agent has the required tools:

- python3
- pip3
- git
- docker
- docker compose
- make
- jq

### Prepare CI Env File

Creates a CI-local `.env` in the workspace so Compose and test commands have the expected variables without depending on a developer-local `.env`.

### Validate Compose Configuration

Runs Compose rendering validation before using any Compose service.

### Prepare Python

Creates `.venv` and installs the project dependencies.

### Prepare Test Database

Ensures PostgreSQL is available and recreates:

- `opsledger_test`

### Run Tests

Runs the project pytest suite with:

- terminal coverage output
- HTML coverage output
- JUnit XML output

## Current Output and Artifacts

The pipeline currently publishes:

- JUnit XML test results
- archived test output
- archived coverage HTML report

Artifacts are generated under:

- `validation/test-results/phase-08/`

Expected files include:

- `pytest-output.txt`
- `junit.xml`
- `htmlcov/`

## Current Plugin Baseline

The Jenkins plugin baseline required by this phase is:

- `workflow-aggregator`
- `pipeline-stage-view`
- `git`
- `credentials`
- `matrix-auth`
- `docker-workflow`
- `pipeline-utility-steps`
- `junit`
- `timestamper`

## Validation Expectations for Phase 08

A successful Phase 08 run should show:

- pipeline job created in Jenkins
- checkout from SCM
- execution on the static agent
- environment validation passed
- Compose configuration validation passed
- PostgreSQL test database recreated
- pytest passed
- JUnit results visible in Jenkins
- archived artifacts visible in Jenkins

## What Is Still Intentionally Deferred

This phase does not yet implement:

- automated image build/publish stage
- deployment stage
- Nginx switch logic
- blue/green deployment
- rollback automation

Those remain future phases by design.

## Next Pipeline Direction

The next phase should extend the current CI baseline toward:

- image build validation
- stronger artifact handling
- deployment orchestration groundwork

The eventual long-term flow remains:

1. Checkout source
2. Create/activate Python environment
3. Install dependencies
4. Run tests
5. Build application image
6. Deploy inactive color
7. Run health validation
8. Switch Nginx upstream
9. Keep previous color available for rollback

Phase 08 implements the CI portion of that roadmap without yet crossing into deployment automation.