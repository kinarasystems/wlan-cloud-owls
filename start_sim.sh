#!/bin/bash
set -e

SIM_ID="${1:?Usage: $0 <sim-id>}"

API_KEY=$(echo -n "https://localhost:16007" | sha256sum | awk '{print $1}')

RESPONSE=$(curl -sk -X POST "https://localhost:17007/api/v1/operation/${SIM_ID}?operation=start" \
    -H "X-INTERNAL-NAME: owls" \
    -H "X-API-KEY: $API_KEY")

echo "$RESPONSE" | python3 -c "import sys,json; print(json.loads(sys.stdin.read())['id'])"
