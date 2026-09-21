from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.database import create_db_and_tables
from app.routes.patients import router as patient_router
from app.routes.doctors import router as doctor_router
from app.routes.departments import router as department_router
from app.routes.appointments import router as appointment_router
from app.routes import ai
from app.routes import auth


app = FastAPI(
    title="AI Healthcare Assistant",
    description="Healthcare Assistant API",
    version="1.0.0"
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


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def home():
    return {
        "message": "AI Healthcare Assistant API is running"
    }