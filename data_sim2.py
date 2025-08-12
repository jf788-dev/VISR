#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time
import json
import random

# --- MQTT ---
BROKER = "198.18.5.150"
PORT = 1883
TOPIC = "radiation/detectors"   # one topic for all detectors

# --- Detectors ---
DETECTORS = [
    {"sensor_id": "ORTEC01", "lat": 51.5072, "lon": -0.1276},
    {"sensor_id": "ORTEC02", "lat": 50.5072, "lon": -1.1276},
    {"sensor_id": "ORTEC03", "lat": 49.5072, "lon": -2.1276},
]

# Baseline & noise
GAMMA_BASE = 120
NEUTRON_BASE = 3
GAMMA_NOISE = 12
NEUTRON_NOISE = 0.7

# Alarm thresholds
GAMMA_ALARM_CPS = 600
NEUTRON_ALARM_CPS = 20

# Dose rate conversion
U_SV_PER_CPS_GAMMA = 0.005
U_SV_PER_CPS_NEUTRON = 0.02

def simulate_readings():
    gamma_cps = max(0.0, round(random.gauss(GAMMA_BASE, GAMMA_NOISE), 2))
    neutron_cps = max(0.0, round(random.gauss(NEUTRON_BASE, NEUTRON_NOISE), 2))

    gamma_uSv = round(gamma_cps * U_SV_PER_CPS_GAMMA, 3)
    neutron_uSv = round(neutron_cps * U_SV_PER_CPS_NEUTRON, 3)

    return {
        "gamma_count_rate_cps": gamma_cps,
        "gamma_dose_rate_uSv_h": gamma_uSv,
        "gamma_dose_rate_mrem_h": round(gamma_uSv * 0.1, 3),
        "gamma_alarm": gamma_cps >= GAMMA_ALARM_CPS,

        "neutron_count_rate_cps": neutron_cps,
        "neutron_dose_rate_uSv_h": neutron_uSv,
        "neutron_dose_rate_mrem_h": round(neutron_uSv * 0.1, 3),
        "neutron_alarm": neutron_cps >= NEUTRON_ALARM_CPS,
    }

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

try:
    while True:
        for d in DETECTORS:
            fields = simulate_readings()
            payload = {
                "sensor_id": d["sensor_id"],   # becomes a tag (via Telegraf)
                "latitude": float(d["lat"]),          # fields for geomap
                "longitude": float(d["lon"]),
                **fields
            }
            client.publish(TOPIC, json.dumps(payload))
            print("Published:", payload)
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    client.disconnect()