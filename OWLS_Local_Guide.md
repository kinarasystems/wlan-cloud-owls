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

**Step 1 — Create a simulation:**

```bash
SIM_ID=$(./create_sim.sh sample_data/simulation.json)
```

Edit `sample_data/simulation.json` to adjust the simulation parameters before running.

**Step 2 — Start the simulation:**

```bash
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

