import paho.mqtt.client as mqtt
import time
import json
import random

# Configuration
BROKER = "localhost"  # or IP of your broker
TOPIC = "radiation/detectors"

# Detector configurations (mean, std_dev)
detectors = {
    "detector-1": (100, 10),
    "detector-2": (250, 25),
    "detector-3": (400, 40)
}

# MQTT client
client = mqtt.Client()
client.connect(BROKER, 1883, 60)

# Send data every second
try:
    while True:
        for detector_id, (mean, stddev) in detectors.items():
            count_rate = max(0, round(random.gauss(mean, stddev), 2))
            payload = {
                "sensor_id": detector_id,
                "count_rate": count_rate
            }
            client.publish(TOPIC, json.dumps(payload))
            print(f"Published: {payload}")
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped.")
    client.disconnect()