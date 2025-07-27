#!/bin/bash

echo "Starting VISR stack..."
docker compose up -d

# Wait a few seconds to ensure services are up
sleep 5

# Open Grafana and InfluxDB in browser
open http://localhost:3000       # Grafana
open http://localhost:8086       # InfluxDB