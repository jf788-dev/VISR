import requests
import re
import numpy as np

DEVICE_URL = "http://198.18.5.144/remote/v1/n4242"

def get_tag_value(xml, tag):
    """Return float value of <tag> ... </tag> from xml string."""
    m = re.search(rf"<{tag}>\s*([+-]?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?)\s*</{tag}>", xml)
    return float(m.group(1)) if m else None

try:
    # Fetch JSON from device
    response = requests.get(DEVICE_URL, timeout=5)
    response.raise_for_status()
    data = response.json()

    # Extract n42XML
    xml_text = data.get("n42XML", "")
    if not xml_text:
        raise ValueError("No n42XML field found in response")

    # --- Parse spectrum counts (largest numeric block) ---
    num_re = r"[+-]?\d+(?:\.\d+)?(?:[Ee][+-]?\d+)?"
    counts_blocks = re.findall(rf"(?:{num_re})(?:\s+{num_re}){{10,}}", xml_text)
    if not counts_blocks:
        raise ValueError("No channel counts found in n42XML")
    counts_str = max(counts_blocks, key=len)
    counts = np.array([float(x) for x in counts_str.split()], dtype=float)

    # --- Get calibration coefficients from XML tags ---
    offset = get_tag_value(xml_text, "OffsetValue") or 0.0
    gain = get_tag_value(xml_text, "GainValue") or 1.0
    quad = get_tag_value(xml_text, "QuadraticCoefficient") or 0.0

    # --- Transform channels to energies ---
    ch = np.arange(len(counts), dtype=float)
    energy_keV = offset + gain * ch + quad * (ch ** 2)

    # --- Combine into one NumPy array: [channel, energy, count] ---
    arr = np.column_stack((ch, energy_keV, counts))

    # Print array
    print(arr)

except Exception as e:
    print("Error:", e)