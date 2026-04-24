#!/usr/bin/env bash
set -euo pipefail

ACTIVE_FILE="docker/nginx/conf.d/includes/active_proxy_pass.conf"

if grep -q 'app_blue_backend' "${ACTIVE_FILE}"; then
  echo "blue"
elif grep -q 'app_green_backend' "${ACTIVE_FILE}"; then
  echo "green"
else
  echo "Unable to determine active color from ${ACTIVE_FILE}" >&2
  exit 1
fi
