import os
from contextlib import asynccontextmanager

import psycopg
from fastapi import FastAPI

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app:app@localhost:5432/appdb")


def get_conn():
    return psycopg.connect(DATABASE_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    with get_conn() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS visits "
            "(id SERIAL PRIMARY KEY, ts TIMESTAMPTZ DEFAULT now())"
        )
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/visits")
def add_visit():
    with get_conn() as conn:
        conn.execute("INSERT INTO visits DEFAULT VALUES")
        count = conn.execute("SELECT count(*) FROM visits").fetchone()[0]
    return {"visits": count}


@app.get("/visits")
def get_visits():
    with get_conn() as conn:
        count = conn.execute("SELECT count(*) FROM visits").fetchone()[0]
    return {"visits": count}