#!/bin/bash
set -e

echo "[+] Installing dependencies..."
sudo apt update
sudo apt install -y hostapd

echo "[+] Unmasking and enabling hostapd..."
sudo systemctl unmask hostapd
sudo systemctl enable hostapd

echo "[+] Copying config file..."
sudo cp hostapd.conf /etc/hostapd/hostapd.conf

echo '[+] Updating DAEMON_CONF path...'
sudo sed -i 's|^#DAEMON_CONF=.*|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd

echo "[+] Starting hostapd service..."
sudo systemctl restart hostapd

echo "[+] Setup complete. AP should be active on channel 100 with SSID 'VISR_DFS_AP'"
