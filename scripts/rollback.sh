#!/usr/bin/env bash
set -euo pipefail

COMPOSE_CMD=(docker compose)
if [[ -n "${COMPOSE_PROJECT_NAME:-}" ]]; then
  COMPOSE_CMD=(docker compose -p "${COMPOSE_PROJECT_NAME}")
fi

TARGET_COLOR="${1:-}"

if [[ -z "${TARGET_COLOR}" ]]; then
  CURRENT_COLOR="$(./scripts/get-active-color.sh)"
  if [[ "${CURRENT_COLOR}" == "blue" ]]; then
    TARGET_COLOR="green"
  else
    TARGET_COLOR="blue"
  fi
fi

if [[ "${TARGET_COLOR}" != "blue" && "${TARGET_COLOR}" != "green" ]]; then
  echo "Usage: $0 [blue|green]" >&2
  exit 1
fi

echo "Rollback target: ${TARGET_COLOR}"

./scripts/healthcheck.sh "${TARGET_COLOR}"
./scripts/switch-nginx.sh "${TARGET_COLOR}"

echo "Rollback complete. Active color: $(./scripts/get-active-color.sh)"
