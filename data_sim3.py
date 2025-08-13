import paho.mqtt.client as mqtt
import requests, time, json, random

BROKER = "localhost"
TOPIC = "radiation/detectors"
IPS = ["198.18.5.144", "198.18.5.145", "198.18.5.146"]
TIMEOUT = 5
PERIOD = 1.0
SIMULATE = True  # Set to False for real API calls

FIELDS = {
    "gamma_current_count_rate_cps": {"DetectorType": "Gamma",  "Remark": "Current", "path": ["CountRate", "value"], "type": float},
    "gamma_current_dose_uSv_h":     {"DetectorType": "Gamma",  "Remark": "Current", "path": ["DoseRate", 0, "value"], "type": float},
    "gamma_current_dose_mrem_h":    {"DetectorType": "Gamma",  "Remark": "Current", "path": ["DoseRate", 1, "value"], "type": float},
    "gamma_current_alarm":          {"DetectorType": "Gamma",  "Remark": "Current", "path": ["Alarm"], "type": bool},

    "neutron_current_count_rate_cps": {"Detector": "Neutron", "Remark": "Current", "path": ["CountRate", "value"], "type": float},
    "neutron_current_dose_uSv_h":     {"Detector": "Neutron", "Remark": "Current", "path": ["DoseRate", 0, "value"], "type": float},
    "neutron_current_dose_mrem_h":    {"Detector": "Neutron", "Remark": "Current", "path": ["DoseRate", 1, "value"], "type": float},
    "neutron_current_alarm":          {"Detector": "Neutron", "Remark": "Current", "path": ["Alarm"], "type": bool},

    "location_latitude":  {"path": ["MeasurementLocation", "Coordinates", 0], "type": float},
    "location_longitude": {"path": ["MeasurementLocation", "Coordinates", 1], "type": float},
}

client = mqtt.Client()
client.connect(BROKER, 1883, 60)

def generate_fake_response(ip):
    return {
        "Measurement": {
            "CountDoseData": [
                {
                    "DetectorType": "Gamma",
                    "Detector": "HpGe 67mm x 52mm",
                    "Alarm": random.choice([True, False]),
                    "AlarmDescription": "",
                    "StartTime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "Remark": "Current",
                    "DoseRate": [
                        {"value": round(random.uniform(0.3, 0.5), 6), "unit": "µSv/h"},
                        {"value": round(random.uniform(0.03, 0.05), 6), "unit": "mrem/h"}
                    ],
                    "CountRate": {"value": random.randint(500, 800), "unit": "cps"}
                },
                {
                    "DetectorType": "Li6F/ZnS",
                    "Detector": "Neutron",
                    "Alarm": random.choice([True, False]),
                    "AlarmDescription": "",
                    "StartTime": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "Remark": "Current",
                    "DoseRate": [
                        {"value": round(random.uniform(0.05, 0.2), 6), "unit": "µSv/h"},
                        {"value": round(random.uniform(0.005, 0.02), 6), "unit": "mrem/h"}
                    ],
                    "CountRate": {"value": round(random.uniform(0.1, 1.0), 3), "unit": "cps"}
                }
            ],
            "MeasurementLocation": {"Coordinates": [round(random.uniform(-90, 90), 6),
                                                    round(random.uniform(-180, 180), 6)]}
        }
    }

try:
    while True:
        t0 = time.time()
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        for ip in IPS:
            if SIMULATE:
                data = generate_fake_response(ip)
            else:
                url = f"http://{ip}/remote/v1/measurement/doseCountRate"
                try:
                    r = requests.get(url, timeout=TIMEOUT)
                    r.raise_for_status()
                    data = r.json()
                except Exception as e:
                    print(f"{ip} fetch error: {e}")
                    continue

            meas = data.get("Measurement", {}) if isinstance(data, dict) else {}
            count_data = meas.get("CountDoseData", []) or []

            payload = {"sensor_id": ip, "timestamp": ts}

            for name, spec in FIELDS.items():
                entry = meas
                if ("DetectorType" in spec) or ("Detector" in spec) or ("Remark" in spec):
                    found = {}
                    for e in count_data:
                        if not isinstance(e, dict):
                            continue
                        ok = True
                        for k in ("DetectorType", "Detector", "Remark"):
                            if k in spec:
                                want = spec[k]
                                have = (e.get(k) or "").strip()
                                if have != want:
                                    ok = False
                                    break
                        if ok:
                            found = e
                            break
                    entry = found

                v = entry
                for k in spec["path"]:
                    try:
                        v = v[k]
                    except (TypeError, KeyError, IndexError):
                        v = None
                        break

                t = spec.get("type")
                if t is bool:
                    v = (str(v).strip().lower() in ("1", "true", "yes", "on")) if isinstance(v, str) else bool(v) if v is not None else None
                elif t:
                    try:
                        v = t(v)
                    except (TypeError, ValueError):
                        v = None

                payload[name] = v

            client.publish(TOPIC, json.dumps(payload))
            print("Published:", payload)

        dt = time.time() - t0
        if dt < PERIOD:
            time.sleep(PERIOD - dt)

except KeyboardInterrupt:
    print("Stopped.")
finally:
    client.disconnect()