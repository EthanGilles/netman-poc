#!/usr/bin/env bash
set -euo pipefail

gns3server -L --host "${GNS3_SERVER_HOST}" --port "${GNS3_SERVER_PORT}" > gns3server.log 2>&1 &

echo "Waiting for GNS3 server to accept API connections..."
for i in $(seq 1 20); do
  if curl --silent --fail \
      -u "${GNS3_API_USERNAME}:${GNS3_API_PASSWORD}" \
      "http://${GNS3_SERVER_HOST}:${GNS3_SERVER_PORT}/v2/version" >/dev/null 2>&1; then
    echo "GNS3 server is up"
    exit 0
  fi
  sleep 2
done

echo "GNS3 server failed to start"
cat gns3server.log || true
exit 1
