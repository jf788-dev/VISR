#!/usr/bin/env python3
import paho.mqtt.client as mqtt
import requests
import time
import json

# --- Config ---
BROKER = "localhost"
TOPIC = "radiation/detectors"
DEVICE_URL = "http://198.18.5.144/remote/v1/measurement/doseCountRate"
SENSOR_ID = "ORTEC01"

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

def get_payload():
    r = requests.get(DEVICE_URL, timeout=5)
    r.raise_for_status()
    return r.json()

def pick_entry(rows, det_type):
    for e in rows:
        if e.get("DetectorType") == det_type and e.get("Remark") == "Current":
            return e
    return None

def extract_doserates(entry):
    uSv = None
    mrem = None
    for d in entry.get("DoseRate", []) or []:
        unit = (d.get("unit") or "").replace("Âµ", "µ")
        val = d.get("value")
        if isinstance(val, (int, float)):
            if "µSv/h" in unit or "uSv/h" in unit:
                uSv = float(val)
            elif "mrem/h" in unit:
                mrem = float(val)
    return uSv, mrem

def build_message(doc):
    rows = doc.get("Measurement", {}).get("CountDoseData", []) or []

    gamma = pick_entry(rows, "Gamma")
    neutron = pick_entry(rows, "Neutron")

    msg = {"sensor_id": SENSOR_ID}

    if gamma:
        cr_g = gamma.get("CountRate", {}).get("value")
        uSv, mrem = extract_doserates(gamma)
        msg["gamma_count_rate_cps"] = float(cr_g) if isinstance(cr_g, (int, float)) else None
        msg["gamma_dose_rate_uSv_h"] = uSv
        msg["gamma_dose_rate_mrem_h"] = mrem
        msg["gamma_alarm"] = bool(gamma.get("Alarm", False))

    if neutron:
        cr_n = neutron.get("CountRate", {}).get("value")
        msg["neutron_count_rate_cps"] = float(cr_n) if isinstance(cr_n, (int, float)) else None
        msg["neutron_alarm"] = bool(neutron.get("Alarm", False))

    return msg

# --- Main loop ---
try:
    while True:
        try:
            doc = get_payload()
            payload = build_message(doc)
            client.publish(TOPIC, json.dumps(payload))
            print("Published:", payload)
        except Exception as e:
            print("Error:", e)
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    client.disconnect()