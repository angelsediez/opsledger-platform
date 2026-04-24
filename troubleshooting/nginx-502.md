# Troubleshooting — Nginx 502

## Typical Symptoms

- browser or `curl` receives `502 Bad Gateway`
- Nginx is up, but the current backend is not responding
- blue/green switch may have targeted a color that is not healthy

## Quick Checks

### Check current active color

```bash
./scripts/get-active-color.sh
```

### Check public header using GET

```bash
set -a
source .env
set +a

HEADER_COLOR="$(curl -fsS -D - -o /dev/null "http://127.0.0.1:${NGINX_PORT}/health/live" \
  | tr -d '\r' \
  | awk -F': ' '/^X-OpsLedger-Active-Color:/{print $2}')"

echo "Nginx header color: ${HEADER_COLOR}"
```

### Check Nginx configuration

```bash
docker compose exec nginx nginx -t
```

### Check Nginx logs

```bash
docker compose exec nginx sh -c 'tail -n 50 /var/log/nginx/error.log'
docker compose exec nginx sh -c 'tail -n 50 /var/log/nginx/access.log'
```

### Check app color health

```bash
./scripts/healthcheck.sh blue
./scripts/healthcheck.sh green
```

## Common Causes

- target color container is stopped
- target color healthcheck is failing
- Nginx include points to the wrong backend
- Nginx config was edited manually and is inconsistent

## Recovery

If the active color is unhealthy but the other color is healthy:

```bash
./scripts/rollback.sh
```

If both colors need recovery:

```bash
docker compose up -d --build --remove-orphans postgres app_blue app_green nginx
docker compose exec app_blue alembic upgrade head
```

Then revalidate health.

---

# Troubleshooting — Jenkins Build Fails

## Typical Symptoms

- Jenkins pipeline fails during deploy stages
- Compose bind mounts fail
- `docker compose` behaves differently inside Jenkins than in your shell
- build passes tests but fails at deploy

## Quick Checks

### Validate agent is online

```bash
set -a
source .env
set +a

curl -s -u "${JENKINS_ADMIN_ID}:${JENKINS_ADMIN_PASSWORD}" \
  "http://127.0.0.1:${JENKINS_HTTP_PORT}/computer/${JENKINS_AGENT_NAME}/api/json" \
  | jq '{displayName,offline,temporarilyOffline,assignedLabels}'
```

### Validate agent tools

```bash
docker compose exec jenkins-agent sh -c 'docker --version && docker compose version && git --version && python3 --version && make --version | head -n 1 && jq --version'
```

### Validate host CI root exists

```bash
grep '^HOST_CI_ROOT=' .env
ls -ld /home/angelsediez/jenkins-workspaces
```

## Common Causes

- `HOST_CI_ROOT` missing from `.env`
- Jenkins agent does not mount `${HOST_CI_ROOT}:${HOST_CI_ROOT}`
- bind mounts are interpreted by host Docker daemon, not the agent filesystem
- `COMPOSE_PROJECT_NAME` mismatch between pipeline and scripts
- agent lost connection during build

## Recovery

### Rebuild and restart the agent

```bash
docker compose --profile jenkins-agent up -d --build jenkins-agent
```

### Re-check agent connection

```bash
set -a
source .env
set +a

curl -s -u "${JENKINS_ADMIN_ID}:${JENKINS_ADMIN_PASSWORD}" \
  "http://127.0.0.1:${JENKINS_HTTP_PORT}/computer/${JENKINS_AGENT_NAME}/api/json" \
  | jq '{displayName,offline,temporarilyOffline,assignedLabels}'
```

### Re-run build

Use Jenkins UI or API once the agent is healthy.

---

# Troubleshooting — Common Errors

## Active proxy file missing

**Symptom:**

- `./scripts/get-active-color.sh` fails

**Check:**

```bash
ls -l docker/nginx/conf.d/includes/active_proxy_pass.conf
```

**Recovery:**

- restore the file
- make sure it contains one valid backend only

**Expected initial content:**

```nginx
proxy_pass http://app_blue_backend;
add_header X-OpsLedger-Active-Color blue always;
```

## Invalid active color request

**Symptom:**

```text
Usage: ./scripts/... <blue|green>
```

**Cause:**

- script received an invalid color parameter

**Recovery:**

- use only `blue` or `green`

## Inactive color fails healthcheck

**Symptom:**

- deploy script exits before switch

**Expected behavior:**

- traffic must not switch

**Check active color and public header using GET:**

```bash
./scripts/get-active-color.sh

set -a
source .env
set +a

HEADER_COLOR="$(curl -fsS -D - -o /dev/null "http://127.0.0.1:${NGINX_PORT}/health/live" \
  | tr -d '\r' \
  | awk -F': ' '/^X-OpsLedger-Active-Color:/{print $2}')"

echo "Nginx header color: ${HEADER_COLOR}"
```

## Nginx config test fails

**Symptom:**

- switch script aborts

**Check:**

```bash
docker compose exec nginx nginx -t
```

**Expected behavior:**

- previous include is restored
- traffic stays on the current active color

## Jenkins secret accidentally expected inside CI `.env`

**Symptom:**

- previous pipeline bug around Jenkins variables in generated `.env`

**Current rule:**

- Jenkins-specific variables are not written into CI `.env`

**Recovery:**

- use repository `.env.example` and runtime `.env` for Jenkins service configuration
- keep CI-generated `.env` application-focused only