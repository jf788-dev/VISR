#!/bin/bash
echo "WARNING: This will stop the VISR stack and delete ALL persistent data (InfluxDB, Grafana configs)."
read -p "Are you sure? (y/N): " confirm

if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
    docker compose down -v
    echo "All services stopped and volumes deleted."
else
    echo "Aborted."
fi