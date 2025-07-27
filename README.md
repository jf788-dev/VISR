# VISR Stack: Quick Start Guide

This stack launches a full sensor data pipeline including:
- **Mosquitto** (MQTT broker)
- **Telegraf** (data collection)
- **InfluxDB** (time-series database)
- **Grafana** (dashboard visualization)

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed (includes Docker Compose)
- Git installed
- Access to this GitHub repo

---

## Clone the Repository

<pre>
git clone https://github.com/jf788-dev/VISR.git
cd VISR
</pre>


## Starting, Stopping and Resetting the Stack

```bash
# Clone the repository
git clone https://github.com/jf788-dev/VISR.git
cd VISR

# Start the Docker stack, pulling all required images and launching containers
# Automatically opens Grafana and InfluxDB in the browser
bash start.sh

# Stop the stack (retains all data)
bash stop.sh

# Reset the stack (removes all data and containers for a clean start)
bash reset.sh
```

## Access and Logins

Grafana - https://localhost:3000
Default sign in:
Username: admin
Password: admin

Grafana - https://localhost:8086
Default sign in:
Username: admin
Password: adminpass

## Test Telemetry
<pre>
python3 test_data.py
</pre>

## Setting up InfluxDB Data Source

Login to Grafana as admin using given credentials. Optionally change password. //

Navigate to Data Sources, Add data Source (http://localhost:3000/connections/datasources/new) and select influxdb: 

Query language 'Flux' URL set to http://localhost:8086 turn off 'basic auth'

Set 'Oranization' to VISR

'Token' to visr-token

'Default Bucket' to Data

leave everything else as blank or default and press 'save & test'






