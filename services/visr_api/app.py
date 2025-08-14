from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
import os, psycopg2
from psycopg2.extras import RealDictCursor

DB_DSN = os.environ.get("DB_DSN", "dbname=postgres user=postgres password=admin host=postgres")
API_TOKEN = os.environ.get("API_TOKEN, None")

app = FastAPI(title="VISR Write API")

def db_exec(sql, params=(), fetch=False):
    with psycopg2.connect(DB_DSN) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            if fetch:
                return cur.fetchall()

# ---- simple MVP table (optional) ----
# run this once if you want /notes MVP
try:
    db_exec("""
        CREATE TABLE IF NOT EXISTS notes (
          id BIGSERIAL PRIMARY KEY,
          msg TEXT NOT NULL,
          ts TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
    """)
except Exception:
    pass

# ---- models ----
class IncidentIn(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    severity: str = Field(default="low", pattern="^(low|medium|high|critical)$")
    reported_by: str | None = None  # UUID string allowed; DB will cast

class TaskingIn(BaseModel):
    incident_id: str                 # UUID string
    assigned_to: str | None = None   # UUID string
    description: str = Field(min_length=1)
    priority: str = Field(default="medium", pattern="^(low|medium|high|urgent)$")
    status: str = Field(default="pending", pattern="^(pending|in_progress|completed|cancelled)$")

class NoteIn(BaseModel):
    msg: str = Field(min_length=1)

# ---- token check (dev: optional) ----
@app.middleware("http")
async def auth_mw(request, call_next):
    if API_TOKEN:
        if request.headers.get("x-api-token") != API_TOKEN:
            raise HTTPException(status_code=401, detail="Unauthorized")
    return await call_next(request)

# ---- endpoints ----
@app.post("/incidents")
def create_incident(body: IncidentIn):
    rows = db_exec(
        """
        INSERT INTO incidents (title, description, severity, reported_by)
        VALUES (%s, %s, %s, NULLIF(%s,'')::uuid)
        RETURNING id;
        """,
        (body.title, body.description, body.severity, body.reported_by),
        fetch=True
    )
    return {"ok": True, "id": rows[0]["id"]}

@app.post("/taskings")
def create_tasking(body: TaskingIn):
    rows = db_exec(
        """
        INSERT INTO taskings (incident_id, assigned_to, description, priority, status)
        VALUES (NULLIF(%s,'')::uuid, NULLIF(%s,'')::uuid, %s, %s, %s)
        RETURNING id;
        """,
        (body.incident_id, body.assigned_to, body.description, body.priority, body.status),
        fetch=True
    )
    return {"ok": True, "id": rows[0]["id"]}

@app.post("/notes")
def create_note(body: NoteIn):
    rows = db_exec(
        "INSERT INTO notes (msg) VALUES (%s) RETURNING id, ts;",
        (body.msg,),
        fetch=True
    )
    return {"ok": True, "id": rows[0]["id"], "ts": rows[0]["ts"]}