# Local OpenWifi Load Simulator (OWLS) Guide

This document covers how to compile, deploy, and run simulations with OWLS (OpenWifi Load Simulator) on local machine (VM,bare metal).

## 1. Prerequisites

### Certificate Requirements

1. Obtain a simulator certificate and trust chain from any functional AP or obtain simulation device package from Insta.
2. Rename them:
   - `operational.pem` -> `device-cert.pem`
   - `key.pem` -> `device-key.pem`
   - `root.pem` -> `root.pem`
3. Place files in the `certs/` directory of your OWLS data folder.
4. Create `certs/cas/` directory.

## 2. Compiling OWLS

The project includes a multi-stage Dockerfile for building OWLS:

```bash
docker build --no-cache -t owls:latest .
```

## 3. Deploying OWLS on local machine

Use the provided script `run_local_owls.sh`, passing the gateway hostname as the only argument:

```bash
./run_local_owls.sh cgw-kiccgw.dev.kinsights.io
```

The script resolves the gateway IP and maps it inside the container via `--add-host`. Certificates and data are mounted from `certs/` and `data/` relative to the script location.

## 4. Creating and Running Simulations

To create and run simulation use OWLS REST API. Base URL: `https://localhost:16007/api/v1`

**Quick start — create and run in one step:**

```bash
./run_sim.sh sample_data/simulation.json
```

Edit `sample_data/simulation.json` to adjust the simulation parameters before running. The script will output the simulation and running IDs along with commands for status, stop, and delete.

**Or run each step individually:**

```bash
SIM_ID=$(./create_sim.sh sample_data/simulation.json)
RUNNING_ID=$(./start_sim.sh $SIM_ID)
```

**Check status:**

```bash
./sim_status.sh $RUNNING_ID
```

**Stop:**

```bash
./stop_sim.sh $SIM_ID $RUNNING_ID
```

**Delete simulation definition:**

```bash
./delete_sim.sh $SIM_ID
```

## 5. Scale Testing

OWLS supports large-scale simulation testing with thousands of simulated APs. The following tools and configuration options are available to help run and monitor scale tests.

### Simulation Configuration

The simulation JSON (`sample_data/simulation.json`) supports the following parameters:

| Parameter | Description |
|---|---|
| `name` | Simulation name |
| `deviceType` | AP device type to simulate |
| `devices` | Number of simulated APs |
| `gateway` | Gateway URL (with port 15002) |
| `macPrefix` | MAC address prefix for simulated devices |
| `simulationLength` | Duration of the simulation in seconds |
| `minAssociations` / `maxAssociations` | Range of associated SSIDs per AP |
| `minClients` / `maxClients` | Range of connected clients per AP |
| `stateInterval` | Interval (in seconds) between state reports |
| `healthCheckInterval` | Interval (in seconds) between health check reports |

### Monitoring Scripts

- **`monitor_top.sh`** — Continuously snapshots `kubectl top pods` and `kubectl top nodes` for a given namespace, appending timestamped blocks to a log file. Usage: `./monitor_top.sh <namespace> [interval_seconds] [output_file]`
- **`collect_data.sh`** — Quick inline monitor loop that logs pod and node resource usage every 2 seconds.

### Running a Scale Test

1. Configure your simulation parameters in `sample_data/simulation.json`, adjusting `devices`, `stateInterval`, and `healthCheckInterval` for your target scale.
2. Start resource monitoring in a separate terminal: `./monitor_top.sh <namespace>`
3. Launch the simulation via the OWLS UI or REST API.
4. Review the monitor log to analyze resource consumption over time.
