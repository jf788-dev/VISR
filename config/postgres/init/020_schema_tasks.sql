-- 020_schema_status.sql
-- Rolling network/status logs for any asset

CREATE TABLE IF NOT EXISTS asset_network_status (
  id BIGSERIAL PRIMARY KEY,
  asset_id UUID NOT NULL REFERENCES assets(id) ON DELETE CASCADE,
  ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),

  -- networking (historical)
  ip INET,
  mac MACADDR,
  interface TEXT,                                    -- eth0, wlan0, mpu5, etc.
  link_state TEXT CHECK (link_state IN ('up','down','degraded')),

  -- link quality
  rssi INT,                                          -- dBm
  snr NUMERIC(6,2),                                  -- dB
  tx_rate_mbps NUMERIC(10,3),
  rx_rate_mbps NUMERIC(10,3),
  latency_ms NUMERIC(10,3),
  jitter_ms NUMERIC(10,3),
  packet_loss_pct NUMERIC(6,3),

  -- device & location
  battery_pct NUMERIC(5,2),
  latitude DOUBLE PRECISION,
  longitude DOUBLE PRECISION,
  altitude_m DOUBLE PRECISION,

  -- ad hoc fields per entry
  extra JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Helpful indexes (optional but recommended)
CREATE INDEX IF NOT EXISTS idx_status_asset_ts ON asset_network_status(asset_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_status_ip ON asset_network_status(ip);