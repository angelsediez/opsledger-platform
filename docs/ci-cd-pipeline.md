# CI/CD Pipeline

## Purpose

This document describes the current CI/CD shape of the OpsLedger Platform project.

As of Phase 10, the project has:

- a functional Jenkins CI pipeline
- a local blue/green deployment flow
- Nginx-based traffic switching
- rollback hardening
- deploy-failure simulation
- manual runbooks and troubleshooting support

The goal of this document is to define clearly what is implemented now and what remains intentionally deferred.

## Current Pipeline Model

The pipeline is defined in:

- `Jenkinsfile`

The Jenkins job is configured as:

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

## Current Pipeline Scope

At the current phase, the pipeline can do both:

- CI validation
- local blue/green deployment

The pipeline includes the parameter:

- `RUN_DEPLOY`

Behavior:

- `RUN_DEPLOY=false` → CI only
- `RUN_DEPLOY=true` → CI + local blue/green deploy

## Implemented Pipeline Stages

1. Checkout source
2. Validate tools and runtime environment
3. Prepare CI `.env`
4. Validate Docker Compose configuration
5. Prepare Python virtual environment
6. Prepare PostgreSQL test database
7. Run pytest with coverage and JUnit XML output
8. Deploy inactive color
9. Verify switched traffic through Nginx

## Stage Intent

### Checkout

Performs checkout from SCM into a host-mounted CI workspace.

The current workspace path used by Jenkins is:

- `/home/angelsediez/jenkins-workspaces/opsledger-ci-workspace`

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

Current rule:

- Jenkins-specific variables and secrets are not written into the CI `.env`

That includes:

- `JENKINS_HTTP_PORT`
- `JENKINS_ADMIN_ID`
- `JENKINS_ADMIN_PASSWORD`
- `JENKINS_AGENT_NAME`
- `JENKINS_AGENT_SECRET`

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

### Deploy Inactive Color

When `RUN_DEPLOY=true`, the pipeline:

1. ensures the app stack is up
2. deploys or recreates the inactive color
3. validates health on the inactive color
4. switches Nginx traffic
5. keeps the previous color running

### Verify Switched Traffic

After the switch, the pipeline validates:

- public `/health/ready`
- active color response header from Nginx

## Blue/Green Deployment Model in the Pipeline

The deployment portion of the pipeline works with:

- `app_blue`
- `app_green`
- `nginx`
- `postgres`

The flow is:

1. detect current active color
2. choose inactive color
3. deploy inactive color
4. validate `/health/ready`
5. switch Nginx to the new color
6. verify public traffic through Nginx
7. leave previous color available for rollback

## Nginx Switch Model

Nginx owns the public entrypoint and controls traffic using the included file:

- `docker/nginx/conf.d/includes/active_proxy_pass.conf`

The initial active config points to blue:

- `proxy_pass http://app_blue_backend;`
- `add_header X-OpsLedger-Active-Color blue always;`

During deploy or rollback, the pipeline and scripts update that file, validate Nginx config, and reload Nginx.

## Jenkins + Bind Mount Strategy

Because Jenkins uses the host Docker socket, Docker bind mounts are interpreted by the host daemon, not by the filesystem inside the Jenkins agent container.

That means the pipeline cannot safely run deploy commands from a workspace that exists only inside the agent container.

For this reason, the project uses a host-mounted CI root:

- `HOST_CI_ROOT=/home/angelsediez/jenkins-workspaces`

The Jenkins agent mounts:

- `${HOST_CI_ROOT}:${HOST_CI_ROOT}`

The pipeline checks out the repository into:

- `${HOST_CI_ROOT}/opsledger-ci-workspace`

This is required so Compose bind mounts for files such as the Nginx config work correctly during Jenkins-driven deploys.

## Current Output and Artifacts

The project currently publishes or stores:

- JUnit XML test results
- archived pytest output
- archived HTML coverage report
- archived blue/green healthcheck logs
- manual validation logs from rollback hardening and deploy-failure simulation

Operational evidence roots include:

- `validation/test-results/phase-08/`
- `validation/test-results/phase-10/`
- `validation/healthcheck-logs/phase-09/`
- `validation/healthcheck-logs/phase-10/`

Expected files include:

- `pytest-output.txt`
- `junit.xml`
- `htmlcov/`
- healthcheck logs for blue/green validation
- healthcheck logs for rollback hardening and failure simulation

## Current Plugin Baseline

The Jenkins plugin baseline required by the current pipeline is:

- `workflow-aggregator`
- `pipeline-stage-view`
- `git`
- `credentials`
- `matrix-auth`
- `docker-workflow`
- `pipeline-utility-steps`
- `junit`
- `timestamper`

## Validation Expectations

A successful current-phase run should show:

- pipeline job created in Jenkins
- checkout from SCM
- execution on the static agent
- environment validation passed
- Compose configuration validation passed
- PostgreSQL test database recreated
- pytest passed
- JUnit results visible in Jenkins
- archived artifacts visible in Jenkins
- inactive color deployed successfully
- healthcheck passed before switch
- Nginx switched to the new color
- active color header visible through public traffic
- previous color still available for rollback

Operational validation outside the pipeline should also demonstrate:

- failed deploy simulation does not switch traffic
- previous active color remains serving after failed promotion
- manual rollback succeeds
- recovery runbooks are usable

## Current Operational Boundary

What is implemented now:

- SCM-backed Pipeline as Code
- execution on the static Jenkins agent
- CI validation
- test database recreation
- pytest execution
- JUnit publication
- artifact archiving
- local blue/green deployment
- Nginx traffic switching
- manual rollback path
- rollback hardening
- deploy-failure simulation
- runbooks and troubleshooting as operational support

## What Is Still Intentionally Deferred

This phase does not yet implement:

- registry push
- image promotion workflow
- canary release
- weighted traffic routing
- automatic rollback on deploy failure
- cloud deployment
- Kubernetes rollout logic

Those remain out of scope by design.