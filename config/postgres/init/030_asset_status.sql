CREATE TABLE IF NOT EXISTS public.asset_status (
  id SERIAL PRIMARY KEY,
  asset_id INTEGER UNIQUE REFERENCES assets(id),
  online_status BOOLEAN NOT NULL,
  timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
  round_trip_time DOUBLE PRECISION
);
