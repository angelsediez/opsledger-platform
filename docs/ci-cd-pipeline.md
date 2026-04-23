# CI/CD Pipeline

## Purpose

This document describes the intended CI/CD shape of the OpsLedger Platform project.

At the current phase, the pipeline is not fully implemented yet, but the runtime foundation for CI now exists locally through Jenkins controller + static agent.

The goal of this document is to make the pipeline direction explicit before the full `Jenkinsfile` implementation is added.

## Planned Stages

1. Checkout source
2. Create/activate Python environment
3. Install dependencies
4. Run tests
5. Build application image
6. Deploy inactive color
7. Run health validation
8. Switch Nginx upstream
9. Keep previous color available for rollback

## Jenkins Model

- Jenkinsfile in repository
- controller coordinates
- agent executes build/test/deploy tasks

## Phase 07 Update — Jenkins runtime baseline

At Phase 07, the project now has a local Jenkins runtime baseline composed of:

- `jenkins-controller`
- `jenkins-agent`

This does not yet implement the full CI/CD pipeline, but it prepares the environment required to do so cleanly in the next phase.

## Execution Model

The Jenkins runtime follows a controller/agent split:

- controller: orchestration only
- agent: execution node

The controller is configured with:

- `0` executors

This means builds are not intended to run on the controller.

The static agent is the node that should execute future pipeline stages.

## Agent Label Strategy

The static agent is expected to use labels such as:

- `docker`
- `linux`
- `local`

This gives a clean baseline for future `Jenkinsfile` agent selection.

## Why the Agent Matters

The agent is prepared with the tools needed for the next phase of CI work, including:

- Docker CLI
- Docker Compose plugin
- git
- python3
- make
- jq

This makes the agent suitable for:

- source checkout
- dependency installation
- test execution
- image build operations
- local stack validation

## Plugin Baseline

The Jenkins plugin baseline at this phase is intentionally small and focused.

Current plugin set:

- `workflow-aggregator`
- `pipeline-stage-view`
- `git`
- `credentials`
- `matrix-auth`
- `docker-workflow`
- `pipeline-utility-steps`

This is enough to support the transition into Pipeline-as-Code without overloading the local-lab Jenkins environment.

## Local-Lab Tradeoff

The Jenkins agent mounts the host Docker socket:

- `/var/run/docker.sock`

This is accepted only as a local-lab tradeoff so the agent can interact with the local Docker environment directly.

This should be treated as:

- practical for a portfolio lab
- useful for local CI/CD demonstration
- not equivalent to production-grade isolation

## Current Phase Boundary

At Phase 07, Jenkins runtime is present, but the actual CI pipeline is still pending.

That means:

### Already in place
- Jenkins controller
- Jenkins static agent
- plugin baseline
- controller login
- agent connectivity
- Docker-capable execution node
- repository `Jenkinsfile` placeholder

### Not implemented yet
- real pipeline stages
- automated test execution from Jenkins
- automated image build from Jenkins
- automated deployment flow from Jenkins
- blue/green switching
- rollback automation

## Expected Pipeline Direction for the Next Phase

The next phase should turn the runtime baseline into a working CI pipeline driven by the repository `Jenkinsfile`.

The expected near-term flow is:

1. checkout repository
2. run Python dependency installation
3. run pytest suite
4. build application image
5. validate build output
6. prepare later deployment steps

## Relationship to Later Deployment Phases

The current planned stages already reflect the final intended direction:

1. Checkout source
2. Create/activate Python environment
3. Install dependencies
4. Run tests
5. Build application image
6. Deploy inactive color
7. Run health validation
8. Switch Nginx upstream
9. Keep previous color available for rollback

However, phases 08+ will progressively split these into:

- CI baseline
- deploy orchestration
- switch logic
- rollback logic

## Pipeline Design Constraints

The CI/CD design must keep the same project constraints already established:

- local-first
- no Kubernetes
- no cloud dependency
- Jenkins controller + static agent
- Nginx remains the public app entrypoint
- PostgreSQL remains on host port `5433`
- app-to-postgres traffic remains internal:
  - `postgres:5432`
- Python PostgreSQL driver remains:
  - `psycopg[binary]==3.3.3`

## Validation Expectations for Phase 07

At the current phase, Jenkins validation should confirm:

- controller is up
- controller login is reachable
- controller has plugin baseline installed
- controller is not the main execution node
- agent is connected and online
- agent has required local build tools
- Jenkins runtime is ready for `Jenkinsfile` implementation

## Summary

Phase 07 does not yet deliver the full CI/CD pipeline.

What it does deliver is the required runtime foundation:

- controller
- static agent
- plugin baseline
- execution model
- Docker-capable build node
- clean transition point into Pipeline-as-Code

This is the correct stopping point before implementing the real Jenkins pipeline in the next phase.