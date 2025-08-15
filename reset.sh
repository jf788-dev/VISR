#!/bin/bash
echo "WARNING: This will stop the VISR stack and delete ALL persistent data (InfluxDB, Grafana configs, FileBrowser data)."
read -p "Are you sure? (y/N): " confirm

if [[ "$confirm" == "y" || "$confirm" == "Y" ]]; then
    # Stop stack and remove named volumes
    docker compose down -v

    # Remove FileBrowser bind-mount data
    echo "Clearing FileBrowser data and config..."
    rm -rf ./filebrowser/config/*
    rm -rf ./filebrowser/data/*

    echo "All services stopped, volumes deleted, and FileBrowser data cleared."
else
    echo "Aborted."
fi