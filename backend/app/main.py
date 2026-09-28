
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
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
from app.agent.graph import close_mcp_agents, warmup_rag

CHECKPOINT_DB = (
    Path(__file__).resolve().parents[1]
    / "appointment_checkpoints.sqlite"
)



@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting ODASHA backend...", flush=True)

    create_db_and_tables()

    print("Starting RAG warmup...", flush=True)
    warmup_rag()
    print("RAG warmup finished.", flush=True)

    async with AsyncSqliteSaver.from_conn_string(
        str(CHECKPOINT_DB)
    ) as checkpointer:
        await checkpointer.setup()
        set_appointment_checkpointer(checkpointer)

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


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
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