CREATE TABLE IF NOT EXISTS asset_status (
  id SERIAL PRIMARY KEY,
  asset_ip INET REFERENCES assets(asset_ip),
  online_status BOOLEAN NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
  round_trip_time DOUBLE PRECISION
);

