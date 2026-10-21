import os
from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DATABASE_URL = os.environ["DATABASE_URL"]

def get_conn():
    return psycopg.connect(DATABASE_URL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    with get_conn() as conn:
        conn.execute(
    """CREATE TABLE IF NOT EXISTS tasks(
    id SERIAL PRIMARY KEY,
    title text NOT NULL,
    done boolean NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )
    """
        )
    yield

app = FastAPI(title="tasks", lifespan=lifespan)

class TaskIn(BaseModel):
    title: str

@app.get("/health")
def health():
    try:
        with get_conn() as conn:
            conn.execute("SELECT 1")
    except psycopg.OperationalError:
        raise HTTPException(status_code=503, detail="database unavailable")
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    with get_conn() as conn:
        rows = conn.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()
    return [{"id": r[0], "title": r[1], "done": r[2]} for r in rows]

@app.post("/tasks", status_code=201)
def create_task(task: TaskIn):
    with get_conn() as conn:
        row = conn.execute("INSERT INTO tasks (title) VALUES (%s) RETURNING id", (task.title,)).fetchone()
    return {"id": row[0], "title": task.title, "done": False}

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="task not found")
    return {"id": row[0], "title": row[1], "done": row[2]}