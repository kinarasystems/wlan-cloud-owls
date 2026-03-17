#!/bin/bash
set -e

JSON_FILE="${1:?Usage: $0 <simulation.json>}"

if [ ! -f "$JSON_FILE" ]; then
    echo "Error: file not found: $JSON_FILE"
    exit 1
fi

API_KEY=$(echo -n "https://localhost:16007" | sha256sum | awk '{print $1}')

RESPONSE=$(curl -sk -X POST "https://localhost:17007/api/v1/simulation/0" \
    -H "X-INTERNAL-NAME: owls" \
    -H "X-API-KEY: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "@$JSON_FILE")

echo "$RESPONSE" | python3 -c "
import sys, json
r = json.loads(sys.stdin.read())
if 'id' in r:
    print(r['id'])
else:
    print('Error: ' + json.dumps(r), file=sys.stderr)
    sys.exit(1)
"
