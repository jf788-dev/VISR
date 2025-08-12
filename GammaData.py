import paho.mqtt.client as mqtt
import requests
import time
import json
import re

# Configuration
BROKER = "localhost"
TOPIC = "radiation/detectors"
DEVICE_URL = "http://198.18.5.144/remote/v1/measurement/doseCountRate"
SENSOR_ID = "detector-2"



# Setup MQTT client
client = mqtt.Client()
client.connect(BROKER, 1883, 60)

# Get the Gamma count rate where Remark == "Current"
def get_count_rate():
    try:
        response = requests.get(DEVICE_URL, timeout=5)
        response.raise_for_status()
        data = response.json()

        count_data = data.get("Measurement", {}).get("CountDoseData", [])
 
        for entry in count_data:
            if (
                entry.get("DetectorType") == "Gamma" and
                entry.get("Remark") == "Current"
            ):
                return float(round(entry["CountRate"]["value"]))
    
        print("Gamma Current CountRate not found.")
        return None
    except Exception as e:
        print("Error fetching/parsing data:", e)
        return None

def get_count_rate_2():
    try:
        response = requests.get(DEVICE_URL, timeout=5)
        response.raise_for_status()
        data = response.json()

        count_data = data.get("Measurement", {}).get("CountDoseData", [])
 
        for entry in count_data:

            if (
                entry.get("DetectorType") == "Neutron" and
                entry.get("Remark") == "Current"
            ):
                return float(entry["CountRate"]["value"])

        print("Neutron Current CountRate not found.")
        return None
    except Exception as e:
        print("Error fetching/parsing data:", e)
        return None
# Main loop: fetch & publish once per second
try:
    while True:
        count_rate = get_count_rate()
        count_rate_2 = get_count_rate_2()
        if count_rate is not None:
            payload = {
                "sensor_id": SENSOR_ID,
                "count_rate": count_rate,
                "count_rate_2": count_rate_2
            }
            client.publish(TOPIC, json.dumps(payload))
            print(f"Published: {payload}")
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped.")
    client.disconnect()