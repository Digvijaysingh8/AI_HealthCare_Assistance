import os
from contextlib import AsyncExitStack, asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from app.database.database import create_db_and_tables
from app.agent.appointment_flow import set_appointment_checkpointer
from app.routes.patients import router as patient_router
from app.routes.doctors import router as doctor_router
from app.routes.departments import router as department_router
from app.routes.appointments import router as appointment_router
from app.routes import ai
from app.routes import auth
from app.agent.graph import close_mcp_agents

CHECKPOINT_DB = (
    Path(__file__).resolve().parents[1]
    / "appointment_checkpoints.sqlite"
)




@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting ODASHA backend...", flush=True)

    create_db_and_tables()

    # Retrieval scores pre-tokenized chunks in memory, so indexing the
    # knowledge base here costs a few milliseconds. Doing it at startup keeps
    # the first chat request from paying for it.
    from app.agent.graph import warmup_rag

    warmup_rag()

    # The checkpointer writes a SQLite file next to the app. If that location
    # is not writable (read-only or ephemeral container filesystem), let the
    # API still come up rather than dying before uvicorn binds a port.
    # The try covers setup only; an error while serving must still propagate.
    async with AsyncExitStack() as stack:
        try:
            CHECKPOINT_DB.parent.mkdir(parents=True, exist_ok=True)

            checkpointer = await stack.enter_async_context(
                AsyncSqliteSaver.from_conn_string(str(CHECKPOINT_DB))
            )
            await checkpointer.setup()
            set_appointment_checkpointer(checkpointer)
        except Exception as exc:
            print(
                f"WARNING: appointment checkpointer unavailable ({exc}). "
                "AI assistant features will not work; the rest of the API is up.",
                flush=True,
            )

        try:
            yield
        finally:
            await close_mcp_agents()

app = FastAPI(
    title="AI Healthcare Assistant",
    description="Healthcare Assistant API",
    version="1.0.0",
    lifespan=lifespan
)
frontend_url = os.getenv(
    "FRONTEND_URL",
    "http://localhost:5173"
)

# FRONTEND_URL may be a comma-separated list so staging and production
# origins can both be allowed without redeploying.
allowed_origins = [
    origin.strip()
    for origin in frontend_url.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins + [
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(patient_router)
app.include_router(doctor_router)
app.include_router(department_router)
app.include_router(appointment_router)
app.include_router(ai.router)
app.include_router(auth.router)


@app.get("/")
def home():
    return {
        "message": "AI Healthcare Assistant API is running"
    }


@app.get("/health")
def health():
    """Liveness plus a real database round-trip.

    The frontend polls this endpoint, so it reports connectivity problems
    here instead of surfacing them as opaque failed requests.
    """
    from sqlalchemy import text

    from app.database.database import (
        DEFAULT_SQLITE_URL,
        DATABASE_URL,
        engine,
    )

    # A SQLite fallback connects fine, so a bare "connected" would read as
    # healthy while actually serving an empty file with none of the MySQL
    # data. Name the backend so that case is obvious.
    on_sqlite_fallback = DATABASE_URL == DEFAULT_SQLITE_URL
    dialect = "sqlite-fallback" if on_sqlite_fallback \
        else engine.dialect.name

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as exc:
        # 503 so a load balancer or the frontend can react to it.
        raise HTTPException(
            status_code=503,
            detail=f"Database unavailable: {exc}"
        )

    if on_sqlite_fallback:
        # Still 200 so the process is not killed by a health check, but the
        # body says the data is not the real database.
        return {
            "status": "degraded",
            "database": dialect,
            "detail": "DATABASE_URI is not set; using an empty local "
                      "SQLite file instead of the real database.",
        }

    return {"status": "ok", "database": dialect}