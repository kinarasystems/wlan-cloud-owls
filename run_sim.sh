#!/bin/bash
set -e

JSON_FILE="${1:?Usage: $0 <simulation.json>}"

if [ ! -f "$JSON_FILE" ]; then
    echo "Error: file not found: $JSON_FILE"
    exit 1
fi

echo "Creating simulation from $JSON_FILE..."
SIM_ID=$(./create_sim.sh "$JSON_FILE")
echo "Created simulation: $SIM_ID"

echo "Starting simulation..."
RUNNING_ID=$(./start_sim.sh "$SIM_ID")
echo "Simulation running: $RUNNING_ID"

echo ""
echo "To check status:  ./sim_status.sh $RUNNING_ID"
echo "To stop:          ./stop_sim.sh $SIM_ID $RUNNING_ID"
echo "To delete:        ./delete_sim.sh $SIM_ID"
