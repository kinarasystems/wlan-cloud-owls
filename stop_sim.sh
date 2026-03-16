#!/bin/bash
set -e

SIM_ID="${1:?Usage: $0 <sim-id> <running-id>}"
RUNNING_ID="${2:?Usage: $0 <sim-id> <running-id>}"

API_KEY=$(echo -n "https://localhost:16007" | sha256sum | awk '{print $1}')

curl -sk -X POST "https://localhost:17007/api/v1/operation/${SIM_ID}?operation=stop&runningId=${RUNNING_ID}" \
    -H "X-INTERNAL-NAME: owls" \
    -H "X-API-KEY: $API_KEY"
