#!/usr/bin/env bash
set -euo pipefail

COMPOSE_CMD=(docker compose)
if [[ -n "${COMPOSE_PROJECT_NAME:-}" ]]; then
  COMPOSE_CMD=(docker compose -p "${COMPOSE_PROJECT_NAME}")
fi

CURRENT_COLOR="$(./scripts/get-active-color.sh)"
TARGET_COLOR="${1:-}"

if [[ -z "${TARGET_COLOR}" ]]; then
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

if [[ "${TARGET_COLOR}" == "${CURRENT_COLOR}" ]]; then
  echo "Rollback target ${TARGET_COLOR} is already active. No action required."
  exit 0
fi

echo "Current active color: ${CURRENT_COLOR}"
echo "Rollback target color: ${TARGET_COLOR}"
echo "Previous color after rollback would become: ${CURRENT_COLOR}"

./scripts/healthcheck.sh "${TARGET_COLOR}"
./scripts/switch-nginx.sh "${TARGET_COLOR}"

echo "Rollback completed successfully"
echo "New active color: $(./scripts/get-active-color.sh)"
