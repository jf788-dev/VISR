-- Core extensions you’ll use
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";   -- UUIDs
CREATE EXTENSION IF NOT EXISTS pg_trgm;       -- for fast LIKE/ILIKE on names
-- If you decide to use PostGIS later, add:
-- CREATE EXTENSION IF NOT EXISTS postgis;