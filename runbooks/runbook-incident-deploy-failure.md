# Runbook — Incident: Deploy Failure on Inactive Color

## Purpose

This runbook describes what to do when a blue/green deploy fails before traffic is switched.

## Goal

The primary goal is:

- confirm the active color did not change
- confirm Nginx still serves the previously healthy color
- recover the inactive color safely
- proceed with rollback or retry only after validation

## Typical Symptoms

You may be in this runbook if:

- `./scripts/deploy-blue-green.sh` exits nonzero
- Jenkins deploy stage fails
- `./scripts/healthcheck.sh <color>` fails
- the inactive color never becomes healthy
- Nginx traffic should not have moved, but you want to prove it

## Immediate Safety Principle

If the inactive color fails healthcheck, traffic must not switch.

That is the expected behavior of this phase.

## Step 1 — Record Current Active Color

```bash
./scripts/get-active-color.sh
```

Store the result mentally as the active color before recovery.

## Step 2 — Validate Public Traffic Is Still on the Previous Color

```bash
set -a
source .env
set +a

HEADER_COLOR="$(curl -fsS -D - -o /dev/null "http://127.0.0.1:${NGINX_PORT}/health/live" \
  | tr -d '\r' \
  | awk -F': ' '/^X-OpsLedger-Active-Color:/{print $2}')"

echo "Nginx header color: ${HEADER_COLOR}"

curl -s "http://127.0.0.1:${NGINX_PORT}/health/ready" | jq
```

Expected result:

- the `X-OpsLedger-Active-Color` header still matches the color from Step 1
- readiness through Nginx still succeeds

## Step 3 — Inspect the Inactive Color

If the current active color is blue, inspect `app_green`.

If the current active color is green, inspect `app_blue`.

Check status:

```bash
docker compose ps
```

Check logs:

```bash
docker compose logs --no-color app_blue
docker compose logs --no-color app_green
```

Check container health directly:

```bash
docker inspect --format='{{json .State.Health}}' $(docker compose ps -q app_blue)
docker inspect --format='{{json .State.Health}}' $(docker compose ps -q app_green)
```

## Step 4 — Recover the Inactive Color

Bring both colors up safely:

```bash
docker compose up -d --build --remove-orphans postgres app_blue app_green nginx
```

Re-run migrations from the agreed migration color:

```bash
docker compose exec app_blue alembic upgrade head
```

Validate the inactive color again:

```bash
./scripts/healthcheck.sh blue
./scripts/healthcheck.sh green
```

## Step 5 — Decide: Retry Deploy or Stay on Current Color

If the inactive color now passes, you can retry the deploy:

```bash
./scripts/deploy-blue-green.sh
```

If the inactive color still fails, do not switch traffic.

Keep the current active color serving until root cause is fixed.

## Step 6 — Validate Final State

Check active color:

```bash
./scripts/get-active-color.sh
```

Check public header using GET:

```bash
set -a
source .env
set +a

HEADER_COLOR="$(curl -fsS -D - -o /dev/null "http://127.0.0.1:${NGINX_PORT}/health/live" \
  | tr -d '\r' \
  | awk -F': ' '/^X-OpsLedger-Active-Color:/{print $2}')"

echo "Nginx header color: ${HEADER_COLOR}"
```

Check public readiness:

```bash
set -a
source .env
set +a

curl -s "http://127.0.0.1:${NGINX_PORT}/health/ready" | jq
```

## Controlled Failure Simulation Reference

For interview/demo purposes, you can simulate a deploy failure without permanently breaking the stack:

```bash
SIMULATE_FAILURE=true ./scripts/deploy-blue-green.sh
```

Expected result:

- deploy exits nonzero
- active color remains unchanged
- Nginx still serves the previous color

## Evidence to Capture

Recommended evidence:

- deploy failure output
- active color before and after failed deploy
- response header showing traffic did not move
- logs of the failed inactive color
- successful recovery or retry

## Notes

This incident model is intentionally local-first:

- no automatic rollback orchestration
- no canary
- no multi-environment release controller
- manual verification is part of the design