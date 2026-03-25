#!/bin/bash
set -e

GATEWAY_HOST="${1:?Usage: $0 <gateway-host>}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Resolve gateway IP
GATEWAY_IP=$(dig +short "$GATEWAY_HOST" | tail -1)
if [ -z "$GATEWAY_IP" ]; then
    echo "Error: could not resolve $GATEWAY_HOST"
    exit 1
fi
echo "Starting OWLS: gateway=$GATEWAY_HOST ($GATEWAY_IP)"

docker run \
    -p 16007:16007 -p 17007:17007 -p 16107:16107 \
    --ulimit nofile=65536:65536 \
    -e TEMPLATE_CONFIG=true \
    -e RUN_CHOWN=true \
    -e KAFKA_ENABLE=false \
    -e UCENTRAL_SECURITY=none \
    -e RESTAPI_HOST_CERT=/owls-data/certs/device-cert.pem \
    -e RESTAPI_HOST_KEY=/owls-data/certs/device-key.pem \
    -e RESTAPI_HOST_KEY_PASSWORD=mypassword \
    -e INTERNAL_RESTAPI_HOST_CERT=/owls-data/certs/device-cert.pem \
    -e INTERNAL_RESTAPI_HOST_KEY=/owls-data/certs/device-key.pem \
    -e INTERNAL_RESTAPI_HOST_KEY_PASSWORD=mypassword \
    -e RESTAPI_HOST_ROOTCA=/owls-data/certs/root.pem \
    -e INTERNAL_RESTAPI_HOST_ROOTCA=/owls-data/certs/root.pem \
    -e SERVICE_KEY=/owls-data/certs/device-key.pem \
    --add-host="${GATEWAY_HOST}:${GATEWAY_IP}" \
    -v "${SCRIPT_DIR}/certs:/owls-data/certs" \
    -v "${SCRIPT_DIR}/data:/owls-data/data" \
    owls:latest
