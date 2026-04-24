#!/usr/bin/env bash
set -euo pipefail

ACTIVE_FILE="docker/nginx/conf.d/includes/active_proxy_pass.conf"

if [[ ! -f "${ACTIVE_FILE}" ]]; then
  echo "Active proxy file not found: ${ACTIVE_FILE}" >&2
  exit 1
fi

mapfile -t MATCHES < <(grep -Eo 'app_(blue|green)_backend' "${ACTIVE_FILE}" | sort -u)

if [[ "${#MATCHES[@]}" -eq 0 ]]; then
  echo "No active backend found in ${ACTIVE_FILE}" >&2
  exit 1
fi

if [[ "${#MATCHES[@]}" -gt 1 ]]; then
  echo "Ambiguous active backend in ${ACTIVE_FILE}: ${MATCHES[*]}" >&2
  exit 1
fi

case "${MATCHES[0]}" in
  app_blue_backend)
    echo "blue"
    ;;
  app_green_backend)
    echo "green"
    ;;
  *)
    echo "Unexpected backend value: ${MATCHES[0]}" >&2
    exit 1
    ;;
esac
