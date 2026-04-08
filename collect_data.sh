#!/bin/bash
while true; do   echo "=== $(date) ===" | tee -a monitor.log;   kubectl top pods -n kiccgw2 | tee -a monitor.log;   echo "---NODES---" | tee -a monitor.log;   kubectl top nodes | tee -a monitor.log;   sleep 2; done
