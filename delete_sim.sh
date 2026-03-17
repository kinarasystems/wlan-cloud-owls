#!/bin/bash
set -e

SIM_ID="${1:?Usage: $0 <sim-id>}"

API_KEY=$(echo -n "https://localhost:16007" | sha256sum | awk '{print $1}')

curl -sk -X DELETE "https://localhost:17007/api/v1/simulation/${SIM_ID}" \
    -H "X-INTERNAL-NAME: owls" \
    -H "X-API-KEY: $API_KEY"
