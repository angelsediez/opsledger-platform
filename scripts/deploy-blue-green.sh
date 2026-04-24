#!/usr/bin/env bash
set -euo pipefail

COMPOSE_CMD=(docker compose)
if [[ -n "${COMPOSE_PROJECT_NAME:-}" ]]; then
  COMPOSE_CMD=(docker compose -p "${COMPOSE_PROJECT_NAME}")
fi

CURRENT_COLOR="$(./scripts/get-active-color.sh)"

if [[ "${CURRENT_COLOR}" == "blue" ]]; then
  TARGET_COLOR="green"
else
  TARGET_COLOR="blue"
fi

PREVIOUS_COLOR="${CURRENT_COLOR}"
TARGET_SERVICE="app_${TARGET_COLOR}"

echo "Current active color: ${CURRENT_COLOR}"
echo "Target inactive color: ${TARGET_COLOR}"
echo "Previous color to preserve for rollback: ${PREVIOUS_COLOR}"

"${COMPOSE_CMD[@]}" up -d --build "${TARGET_SERVICE}"

if [[ "${SIMULATE_FAILURE:-false}" == "true" ]]; then
  echo "Controlled failure simulation enabled"
  echo "Stopping ${TARGET_SERVICE} before promotion healthcheck"
  "${COMPOSE_CMD[@]}" stop "${TARGET_SERVICE}"
fi

if ! ./scripts/healthcheck.sh "${TARGET_COLOR}"; then
  echo "Healthcheck failed for ${TARGET_COLOR}. Traffic switch aborted." >&2
  echo "Active color remains: $(./scripts/get-active-color.sh)"
  exit 1
fi

./scripts/switch-nginx.sh "${TARGET_COLOR}"

echo "Deployment completed successfully"
echo "Current active color: $(./scripts/get-active-color.sh)"
echo "Previous color still available for rollback: ${PREVIOUS_COLOR}"
