import subprocess, re, time, psycopg2

def get_asset_ips():
	try:
		connection = psycopg2.connect(
			dbname="postgres",
			user="postgres",
			password="admin",
			host="localhost",
			port=5432
		)
		cursor = connection.cursor()
		cursor.execute("SELECT asset_ip FROM assets")
		Asset_IPs = cursor.fetchall()
		Asset_IPs = [row[0] for row in Asset_IPs] # Fetch all IPs from the database and save as Tuple
		print(Asset_IPs)
	except Exception as e:
		print(f"An error occurred: {e}")
	finally:
		cursor.close()
		connection.close()

	return Asset_IPs

def write_asset_status(asset_statuses):
	try:
		connection = psycopg2.connect(
			dbname="postgres",
			user="postgres",
			password="admin",
			host="localhost",
			port=5432
		)
		cursor = connection.cursor()
		for status in asset_statuses:
			cursor.execute(
				"""
				INSERT INTO asset_status (asset_ip, online_status, timestamp, round_trip_time)
				VALUES (%s, %s, now(), %s);
				""",
				(status["asset_ip"], status["online_status"], status["round_trip_time"])
			)
		connection.commit()
	except Exception as e:
		print(f"An error occurred: {e}")
	finally:
		cursor.close()
		connection.close()

RTT_RE = re.compile(r'time=([\d.]+) ms')

def ping_once(ip):
    # macOS: use -t for deadline, Linux: use -W
    out = subprocess.run(["ping", "-c", "1", "-t", "1", ip],
                         capture_output=True, text=True)
    if out.returncode == 0:
        m = RTT_RE.search(out.stdout)
        rtt = float(m.group(1)) if m else None
        return True, rtt
    return False, None

while True:
	Asset_IPs = get_asset_ips()
	ping_results = {ip: 0 for ip in Asset_IPs}
	rtt_results = {ip: [] for ip in Asset_IPs}
	for _ in range(2):
		for ip in Asset_IPs:
			ok, rtt = ping_once(ip)
			if ok:
				ping_results[ip] += 1
				if rtt is not None:
					rtt_results[ip].append(rtt)
		time.sleep(1)
	asset_statuses = []
	for ip, count in ping_results.items():
		online_status = count > 0
		avg_rtt = sum(rtt_results[ip]) / len(rtt_results[ip]) if rtt_results[ip] else None
		asset_statuses.append({"asset_ip": ip, "online_status": online_status, "round_trip_time": avg_rtt})
	print(asset_statuses)
	write_asset_status(asset_statuses)