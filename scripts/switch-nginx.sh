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

ACTIVE_FILE="docker/nginx/conf.d/includes/active_proxy_pass.conf"

if [[ ! -f "${ACTIVE_FILE}" ]]; then
  echo "Active proxy file not found: ${ACTIVE_FILE}" >&2
  exit 1
fi

CURRENT_COLOR="$(./scripts/get-active-color.sh)"

if [[ "${CURRENT_COLOR}" == "${COLOR}" ]]; then
  echo "Requested color ${COLOR} is already active. No switch needed."
  exit 0
fi

BACKUP_FILE="$(mktemp)"
cp "${ACTIVE_FILE}" "${BACKUP_FILE}"

cat > "${ACTIVE_FILE}" <<EOF2
proxy_pass http://app_${COLOR}_backend;
add_header X-OpsLedger-Active-Color ${COLOR} always;
EOF2

if ! "${COMPOSE_CMD[@]}" exec -T nginx nginx -t; then
  echo "Nginx config test failed. Restoring previous active configuration." >&2
  cp "${BACKUP_FILE}" "${ACTIVE_FILE}"
  "${COMPOSE_CMD[@]}" exec -T nginx nginx -t >/dev/null
  rm -f "${BACKUP_FILE}"
  exit 1
fi

"${COMPOSE_CMD[@]}" exec -T nginx nginx -s reload
rm -f "${BACKUP_FILE}"

echo "Nginx switch completed"
echo "Previous active color: ${CURRENT_COLOR}"
echo "New active color: ${COLOR}"
