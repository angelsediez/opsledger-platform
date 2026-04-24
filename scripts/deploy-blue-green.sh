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

TARGET_SERVICE="app_${TARGET_COLOR}"

echo "Current active color: ${CURRENT_COLOR}"
echo "Deploying inactive color: ${TARGET_COLOR}"

"${COMPOSE_CMD[@]}" up -d --build "${TARGET_SERVICE}"

./scripts/healthcheck.sh "${TARGET_COLOR}"
./scripts/switch-nginx.sh "${TARGET_COLOR}"

echo "Blue/green switch complete."
echo "New active color: $(./scripts/get-active-color.sh)"
echo "Previous color remains available for immediate rollback: ${CURRENT_COLOR}"
