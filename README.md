# Multi-UAV Formation Flight using MAVLink and ArduPilot SITL

## Introduction
This project demonstrates the implementation of **formation flight control** using multiple simulated drones in **ArduPilot SITL (Software-In-The-Loop)**.  
Three virtual UAVs—one *master* and two *slaves*—are launched in separate instances of SITL, each with a unique MAVLink system ID.  
The goal is to enable the master drone to act as the lead, with slave drones following in formation through synchronized command relay and telemetry sharing via **MAVLink** and **pymavlink**.  
This architecture provides a foundation for scalable multi-agent UAV swarm control used in research, surveillance, and autonomous operations.

---

## Principle of Operation
The formation control system follows a **master–slave synchronization principle** using the **MAVLink protocol**.  
Each UAV runs a separate SITL instance of the ArduCopter firmware. The master UAV transmits its telemetry data, while slave UAVs maintain relative positioning by receiving and replicating key state information such as attitude, position, and velocity.  
Communication between drones occurs via **UDP ports**, managed through **MAVProxy** and **pymavlink** for telemetry forwarding and control automation.

---

## Working

### Step 1 – Simulation Setup
Each drone instance is launched through `sim_vehicle.py`, assigning unique **instance IDs** and **system IDs**, along with separate UDP endpoints for MAVProxy (visualization) and pymavlink (API control).

| Drone | SYSID | MAVProxy Port | pymavlink Port |
|--------|--------|---------------|----------------|
| Master | 1 | 14550 | 14560 |
| Slave 1 | 2 | 14551 | 14561 |
| Slave 2 | 3 | 14552 | 14562 |

Example commands:

```bash
# Terminal 1 – Master Drone
cd ~/ardupilot/ArduCopter
python3 ~/ardupilot/Tools/autotest/sim_vehicle.py -I0 --sysid 1 --out=udp:127.0.0.1:14550 --out=udp:127.0.0.1:14560

# Terminal 2 – Slave Drone 1
cd ~/ardupilot/ArduCopter
python3 ~/ardupilot/Tools/autotest/sim_vehicle.py -I1 --sysid 2 --out=udp:127.0.0.1:14551 --out=udp:127.0.0.1:14561

# Terminal 3 – Slave Drone 2
cd ~/ardupilot/ArduCopter
python3 ~/ardupilot/Tools/autotest/sim_vehicle.py -I2 --sysid 3 --out=udp:127.0.0.1:14552 --out=udp:127.0.0.1:14562
