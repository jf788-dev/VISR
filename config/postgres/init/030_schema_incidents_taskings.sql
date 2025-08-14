-- 030_schema_incidents_taskings.sql
-- Incidents and taskings linked to assets

-- Incidents
CREATE TABLE IF NOT EXISTS incidents (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title TEXT NOT NULL,
  description TEXT,
  severity TEXT CHECK (severity IN ('low','medium','high','critical')) NOT NULL DEFAULT 'low',
  status TEXT CHECK (status IN ('open','in_progress','resolved','closed')) NOT NULL DEFAULT 'open',
  reported_by UUID REFERENCES assets(id) ON DELETE SET NULL,
  ts_reported TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  ts_resolved TIMESTAMPTZ
);

-- Taskings
CREATE TABLE IF NOT EXISTS taskings (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  incident_id UUID REFERENCES incidents(id) ON DELETE CASCADE,
  assigned_to UUID REFERENCES assets(id) ON DELETE SET NULL,
  description TEXT NOT NULL,
  priority TEXT CHECK (priority IN ('low','medium','high','urgent')) NOT NULL DEFAULT 'medium',
  status TEXT CHECK (status IN ('pending','in_progress','completed','cancelled')) NOT NULL DEFAULT 'pending',
  ts_assigned TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  ts_completed TIMESTAMPTZ
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS idx_incidents_status   ON incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_severity ON incidents(severity);
CREATE INDEX IF NOT EXISTS idx_taskings_incident  ON taskings(incident_id);
CREATE INDEX IF NOT EXISTS idx_taskings_assigned  ON taskings(assigned_to);
CREATE INDEX IF NOT EXISTS idx_taskings_status    ON taskings(status);

-- Convenience view: open incidents with their active taskings
CREATE OR REPLACE VIEW open_incidents_with_taskings AS
SELECT
    i.id                AS incident_id,
    i.title             AS incident_title,
    i.severity,
    i.status            AS incident_status,
    i.ts_reported,
    t.id                AS tasking_id,
    t.description       AS tasking_description,
    t.priority          AS tasking_priority,
    t.status            AS tasking_status,
    t.ts_assigned,
    a.asset_name        AS assigned_asset,
    a.asset_type        AS assigned_asset_type
FROM incidents i
LEFT JOIN taskings t
       ON t.incident_id = i.id
LEFT JOIN assets a
       ON a.id = t.assigned_to
WHERE i.status IN ('open','in_progress')
  AND (t.status IS NULL OR t.status IN ('pending','in_progress'))
ORDER BY i.ts_reported DESC, t.ts_assigned DESC;