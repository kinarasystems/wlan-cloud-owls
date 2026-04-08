#!/usr/bin/env bash
# monitor_top.sh — continuously snapshot `kubectl top pods` and `kubectl top nodes`
# for a given namespace, appending timestamped blocks to a log file.
#
# Usage:
#   ./monitor_top.sh <namespace> [interval_seconds] [output_file]
#
# Examples:
#   ./monitor_top.sh kiccgw2
#   ./monitor_top.sh kiccgw2 4 monitor.log
#   ./monitor_top.sh kiccgw2 10 /tmp/my_monitor.log
#
# Defaults:
#   interval  = 4 seconds
#   output    = monitor.log (in current directory)
#
# Stop with Ctrl-C.

set -euo pipefail

NAMESPACE="${1:-}"
INTERVAL="${2:-4}"
OUTPUT="${3:-monitor.log}"

if [[ -z "$NAMESPACE" ]]; then
    echo "Usage: $0 <namespace> [interval_seconds] [output_file]" >&2
    exit 1
fi

# Verify kubectl is available
if ! command -v kubectl &>/dev/null; then
    echo "Error: kubectl not found in PATH" >&2
    exit 1
fi

echo "Monitoring namespace '$NAMESPACE' every ${INTERVAL}s → $OUTPUT"
echo "Press Ctrl-C to stop."
echo ""

snapshot() {
    echo "=== $(date) ==="
    kubectl top pods -n "$NAMESPACE" 2>/dev/null || echo "(kubectl top pods failed)"
}

# Trap Ctrl-C for a clean exit message
trap 'echo ""; echo "Stopped. Log written to: $OUTPUT"' INT

while true; do
    snapshot >> "$OUTPUT"
    sleep "$INTERVAL"
done
