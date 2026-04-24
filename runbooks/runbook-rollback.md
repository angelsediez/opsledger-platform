# Runbook — Manual Rollback

## Purpose

This runbook describes how to perform a manual rollback of traffic between `app_blue` and `app_green` using Nginx as the switch point.

## Scope

Use this runbook when:

- a deploy completed but the new active color is unhealthy
- application behavior regressed after a switch
- you need to return traffic quickly to the previous color
- Jenkins is unavailable and you must operate manually

## Preconditions

Before executing a rollback:

- Nginx is up
- PostgreSQL is up
- both app colors exist in Compose
- the previous color still exists and is recoverable
- you are in the repository root

## Determine Current Active Color

```bash
./scripts/get-active-color.sh
```

Expected output:

```text
blue
```

or

```text
green
```

## Validate the Rollback Target

If the current color is `blue`, the rollback target is usually `green`.

If the current color is `green`, the rollback target is usually `blue`.

Validate the target before switching traffic:

```bash
./scripts/healthcheck.sh blue
./scripts/healthcheck.sh green
```

Only the target color must pass before rollback.

## Execute Rollback

Automatic opposite-color rollback:

```bash
./scripts/rollback.sh
```

Explicit rollback to a chosen color:

```bash
./scripts/rollback.sh blue
./scripts/rollback.sh green
```

## Validate the Rollback

Check the active color in the include file:

```bash
./scripts/get-active-color.sh
```

Check the response header through Nginx using `GET`:

```bash
set -a
source .env
set +a

HEADER_COLOR="$(curl -fsS -D - -o /dev/null "http://127.0.0.1:${NGINX_PORT}/health/live" \
  | tr -d '\r' \
  | awk -F': ' '/^X-OpsLedger-Active-Color:/{print $2}')"

echo "Nginx header color: ${HEADER_COLOR}"
```

Check readiness through Nginx:

```bash
set -a
source .env
set +a

curl -s "http://127.0.0.1:${NGINX_PORT}/health/ready" | jq
```

## Expected Result

A successful rollback means:

- the target color passed healthcheck
- Nginx config test succeeded
- Nginx reloaded successfully
- public traffic now points to the rollback target
- the response header matches the rollback target

## Failure Handling

If rollback does not complete:

- do not keep editing Nginx includes manually without validation

Inspect current active color:

```bash
./scripts/get-active-color.sh
```

Inspect Nginx config:

```bash
docker compose exec nginx nginx -t
```

Inspect both app colors:

```bash
docker compose ps
docker compose logs --no-color app_blue
docker compose logs --no-color app_green
```

Re-run healthcheck only after confirming the target color is actually recoverable.

## Evidence to Capture

Recommended screenshots and evidence:

- current active color before rollback
- rollback command execution
- active color header after rollback
- `/health/ready` after rollback

## Notes

This rollback is intentionally traffic-based and local-lab scoped:

- both colors share one PostgreSQL database
- rollback speed is fast at the proxy layer
- schema compatibility remains a release discipline requirement