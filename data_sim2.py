#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import time, json, random

BROKER = "192.168.1.162"
PORT = 1883
TOPIC_BASE = "radiation/detectors"

DETECTORS = ["ORTEC01", "ORTEC02", "ORTEC03"]
GPS = {"ORTEC01": (51.5074, -0.1278), "ORTEC02": (52.52, 13.405), "ORTEC03": (40.7128, -74.006)}

GAMMA_BASE, GAMMA_NOISE = 120, 12
NEUTRON_BASE, NEUTRON_NOISE = 3, 0.7
GAMMA_ALARM_CPS, NEUTRON_ALARM_CPS = 600, 20
U_SV_PER_CPS_GAMMA, U_SV_PER_CPS_NEUTRON = 0.005, 0.02

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

def sim():
    g = max(0.0, round(random.gauss(GAMMA_BASE, GAMMA_NOISE), 2))
    n = max(0.0, round(random.gauss(NEUTRON_BASE, NEUTRON_NOISE), 2))
    gu = round(g * U_SV_PER_CPS_GAMMA, 3)
    nu = round(n * U_SV_PER_CPS_NEUTRON, 3)
    return {
        "gamma_count_rate_cps": g,
        "gamma_dose_rate_uSv_h": gu,
        "gamma_dose_rate_mrem_h": round(gu * 0.1, 3),
        "gamma_alarm": g >= GAMMA_ALARM_CPS,
        "neutron_count_rate_cps": n,
        "neutron_dose_rate_uSv_h": nu,
        "neutron_dose_rate_mrem_h": round(nu * 0.1, 3),
        "neutron_alarm": n >= NEUTRON_ALARM_CPS,
    }

try:
    while True:
        for det in DETECTORS:
            lat, lon = GPS.get(det, (0.0, 0.0))
            payload = {
                "sensor_id": det,       # tag in Telegraf
                "latitude": lat,
                "longitude": lon,
                **sim()
            }
            # either one topic…
            client.publish(f"{TOPIC_BASE}", json.dumps(payload))
            # …or per-detector topic (handy for topic_tag): client.publish(f"{TOPIC_BASE}/{det}", json.dumps(payload))
            print("Published:", payload)
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    client.disconnect()