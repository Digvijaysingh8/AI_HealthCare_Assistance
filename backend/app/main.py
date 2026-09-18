from fastapi import FastAPI

from app.database.database import create_db_and_tables
from app.routes.patients import router as patient_router
from app.routes.doctors import router as doctor_router
from app.routes.departments import router as department_router
from app.routes.appointments import router as appointment_router
from app.routes import ai



app = FastAPI(
    title="AI Healthcare Assistant",
    description="Healthcare Assistant API",
    version="1.0.0"
)

app.include_router(patient_router)
app.include_router(doctor_router)
app.include_router(department_router)
app.include_router(appointment_router)
app.include_router(ai.router)
@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def home():
    return {
        "message": "AI Healthcare Assistant API is running"
    }