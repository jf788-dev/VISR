CREATE TABLE IF NOT EXISTS public.assets (
  id         SERIAL PRIMARY KEY,
  asset_ip   INET UNIQUE,
  asset_type TEXT NOT NULL CHECK (asset_type IN ('RADIO','SENSOR','EUD')),
  asset_name TEXT NOT NULL UNIQUE,
  operational_status BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_assets_created_at ON public.assets (created_at DESC);