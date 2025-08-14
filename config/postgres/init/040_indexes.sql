-- 040_indexes.sql
-- Practical indexes for assets, status logs, incidents, and taskings

-- ====== ASSETS ======
-- Filter by type and look up by name/IP quickly
CREATE INDEX IF NOT EXISTS idx_assets_type         ON assets(asset_type);
-- Requires pg_trgm (enabled in 000_extensions.sql)
CREATE INDEX IF NOT EXISTS idx_assets_name_trgm    ON assets USING gin (asset_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_assets_asset_ip     ON assets(asset_ip);

-- ====== STATUS LOGS ======
-- Most common query: latest status per asset, time ranges
CREATE INDEX IF NOT EXISTS idx_status_asset_ts     ON asset_network_status(asset_id, ts DESC);
-- Lookups by IP, interface, link state
CREATE INDEX IF NOT EXISTS idx_status_ip           ON asset_network_status(ip);
CREATE INDEX IF NOT EXISTS idx_status_interface    ON asset_network_status(interface);
CREATE INDEX IF NOT EXISTS idx_status_link_state   ON asset_network_status(link_state);
-- Optional JSONB access on ad hoc fields
CREATE INDEX IF NOT EXISTS idx_status_extra_gin    ON asset_network_status USING gin (extra);

-- ====== INCIDENTS ======
CREATE INDEX IF NOT EXISTS idx_incidents_status    ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_severity  ON incidents(severity);
CREATE INDEX IF NOT EXISTS idx_incidents_reported  ON incidents(ts_reported DESC);

-- ====== TASKINGS ======
CREATE INDEX IF NOT EXISTS idx_taskings_incident   ON taskings(incident_id);
CREATE INDEX IF NOT EXISTS idx_taskings_assigned   ON taskings(assigned_to);
CREATE INDEX IF NOT EXISTS idx_taskings_status     ON taskings(status);
CREATE INDEX IF NOT EXISTS idx_taskings_assigned_ts ON taskings(assigned_to, ts_assigned DESC);