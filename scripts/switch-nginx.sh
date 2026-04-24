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

cat > "${ACTIVE_FILE}" <<EOF
proxy_pass http://app_${COLOR}_backend;
add_header X-OpsLedger-Active-Color ${COLOR} always;
EOF

"${COMPOSE_CMD[@]}" exec -T nginx nginx -t
"${COMPOSE_CMD[@]}" exec -T nginx nginx -s reload

echo "Nginx switched to ${COLOR}"
