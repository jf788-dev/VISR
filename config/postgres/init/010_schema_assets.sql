-- Single table for all assets (EUD, RADIO, SENSOR)
CREATE TABLE IF NOT EXISTS assets (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  asset_name TEXT NOT NULL UNIQUE,
  asset_type TEXT NOT NULL CHECK (asset_type IN ('EUD','RADIO','SENSOR')),
  asset_ip INET,
  model TEXT,
  manufacturer TEXT,
  serial_number TEXT,
  firmware_version TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Convenience views by type (pure sugar)
CREATE OR REPLACE VIEW euds    AS SELECT * FROM assets WHERE asset_type = 'EUD';
CREATE OR REPLACE VIEW radios  AS SELECT * FROM assets WHERE asset_type = 'RADIO';
CREATE OR REPLACE VIEW sensors AS SELECT * FROM assets WHERE asset_type = 'SENSOR';