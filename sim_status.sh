#!/bin/bash
set -e

RUNNING_ID="${1:?Usage: $0 <running-id>}"

API_KEY=$(echo -n "https://localhost:16007" | sha256sum | awk '{print $1}')

curl -sk "https://localhost:17007/api/v1/status/${RUNNING_ID}" \
    -H "X-INTERNAL-NAME: owls" \
    -H "X-API-KEY: $API_KEY" | python3 -m json.tool
