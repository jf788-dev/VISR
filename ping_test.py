import time, re, platform, subprocess, psycopg2

# ---- Tunables ----
PING_COUNT     = 5          # one packet per asset per loop
LOOP_INTERVAL  = 2          # seconds between loops
DB             = dict(dbname="postgres", user="postgres", password="admin", host="localhost", port=5432)

# Regex that matches "time=12.3 ms"
RTT_RE = re.compile(r'time=([\d.]+)\s*ms')

def ping_once(ip: str):
    """Return (online: bool, rtt_ms: float|None)."""
    if platform.system().lower().startswith("linux"):
        cmd = ["ping", "-c", str(PING_COUNT), "-W", "1", ip]     # Linux: -W seconds
    else:
        cmd = ["ping", "-c", str(PING_COUNT), "-W", "1000", ip]  # macOS: -W milliseconds
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        return False, None
    m = RTT_RE.search(out.stdout)
    return True, (float(m.group(1)) if m else None)

def main():
    # Single persistent connection
    conn = psycopg2.connect(**DB)
    conn.autocommit = True
    cur = conn.cursor()

    try:
        while True:
            # Fetch current operational assets as (id, ip)
            cur.execute("""
                SELECT id, host(asset_ip)
                FROM public.assets
                WHERE operational_status = TRUE
                  AND asset_ip IS NOT NULL
            """)
            assets = cur.fetchall()  # list[(asset_id, ip)]
            if not assets:
                time.sleep(LOOP_INTERVAL)
                continue

            # Probe each asset once
            rows = []  # list of tuples for executemany
            for asset_id, ip in assets:
                online, rtt = ping_once(ip)
                rows.append((asset_id, online, rtt))
                print(f"{ip} is {'Online' if online else 'Down'}, rtt={rtt}")

            # If no record exists, create new line, if record exists, update.
            cur.executemany("""
                INSERT INTO public.asset_status (asset_id, online_status, timestamp, round_trip_time)
                VALUES (%s, %s, now(), %s)
                ON CONFLICT (asset_id) DO UPDATE SET
                    online_status   = EXCLUDED.online_status,
                    timestamp       = EXCLUDED.timestamp,
                    round_trip_time = EXCLUDED.round_trip_time
            """, rows)

            time.sleep(LOOP_INTERVAL)

    finally:
        # Clean shutdown
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass

if __name__ == "__main__":
    main()