#!/usr/bin/env bash
set -euo pipefail

COLOR="${1:-}"

if [[ "${COLOR}" != "blue" && "${COLOR}" != "green" ]]; then
  echo "Usage: $0 <blue|green>" >&2
  exit 1
fi

COMPOSE_CMD=(docker compose)
if [[ -n "${COMPOSE_PROJECT_NAME:-}" ]]; then
  COMPOSE_CMD=(docker compose -p "${COMPOSE_PROJECT_NAME}")
fi

SERVICE="app_${COLOR}"
LOG_DIR="validation/healthcheck-logs/phase-09"
mkdir -p "${LOG_DIR}"

CID="$("${COMPOSE_CMD[@]}" ps -q "${SERVICE}")"

if [[ -z "${CID}" ]]; then
  echo "Service ${SERVICE} is not running" >&2
  exit 1
fi

echo "Waiting for ${SERVICE} container health..."
for _ in $(seq 1 60); do
  STATUS="$(docker inspect --format='{{.State.Health.Status}}' "${CID}")"
  if [[ "${STATUS}" == "healthy" ]]; then
    break
  fi
  sleep 2
done

STATUS="$(docker inspect --format='{{.State.Health.Status}}' "${CID}")"
if [[ "${STATUS}" != "healthy" ]]; then
  echo "${SERVICE} did not become healthy" >&2
  exit 1
fi

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
LOG_FILE="${LOG_DIR}/${SERVICE}-ready-${TIMESTAMP}.log"

"${COMPOSE_CMD[@]}" exec -T "${SERVICE}" python - <<'PY' | tee "${LOG_FILE}"
import json
import urllib.request

with urllib.request.urlopen("http://127.0.0.1:8000/health/ready", timeout=5) as response:
    payload = json.loads(response.read().decode())
    print(json.dumps(payload, indent=2))
PY
