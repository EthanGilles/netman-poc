#!/usr/bin/env bash
set -euo pipefail

echo "Waiting for 198.51.100.101 (R1) to respond..."
for i in $(seq 1 60); do
  if ping -c 1 -W 3 198.51.100.101 >/dev/null 2>&1; then
    echo "198.51.100.101 (R1) is reachable (attempt $i)"
    exit 0
  fi
  echo "Attempt $i/60 — not yet reachable, waiting 5s..."
  sleep 5
done

echo "Timed out waiting for 198.51.100.101 (R1) after 5 minutes"
exit 1
