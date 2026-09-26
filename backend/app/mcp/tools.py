import os
from mcp.server.mcpserver import MCPServer
from sqlmodel import Session, select
from app.rag.retriever import retrieve_chunks
from app.database.database import engine
from app.services import doctor_service
from datetime import date , datetime
from app.services import appointment_service
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate
import json
mcp = MCPServer("Odasha Healthcare MCP")


def _search_doctors(specialization: str) -> list[dict]:

    with Session(engine) as session:

        doctors = doctor_service.get_doctors(session)

        specialization = specialization.lower().strip()

        results = []

        for doctor in doctors:

            if specialization in doctor.specialization.lower():

                results.append({
                    "id": doctor.id,
                    "name": doctor.name,
                    "specialization": doctor.specialization
                })

        return results

@mcp.tool(name="book_appointment")
def book_appointment(
    doctor_id: int,
    appointment_date: str,
    appointment_time: str,
    confirmation: str
) -> str:
    """Book an appointment for the authenticated patient after explicit confirmation."""

    if not confirmation.strip().upper().startswith("CONFIRM"):
        return json.dumps({
            "error": "Booking requires explicit confirmation."
        })

    user_id = os.getenv("ODASHA_USER_ID")

    if not user_id:
        return json.dumps({
            "error": "Authenticated user context is missing"
        })

    try:
        selected_date = date.fromisoformat(appointment_date)
        selected_time = datetime.strptime(
            appointment_time,
            "%H:%M"
        ).time()

    except ValueError:
        return json.dumps({
            "error": "Invalid date or time format."
        })

    with Session(engine) as session:

        patient = session.exec(
            select(Patient).where(
                Patient.user_id == int(user_id)
            )
        ).first()

        if not patient:
            return json.dumps({
                "error": "Patient profile not found"
            })

        doctor = session.get(Doctor, doctor_id)

        if not doctor:
            return json.dumps({
                "error": "Doctor not found"
            })

        slots = appointment_service.get_available_slots(
            doctor_id,
            selected_date,
            session
        )

        requested_slot = next(
            (
                slot
                for slot in slots
                if slot["time"] == appointment_time
            ),
            None
        )

        if not requested_slot:
            return json.dumps({
                "error": "Requested appointment time is not a valid slot."
            })

        if not requested_slot["available"]:
            return json.dumps({
                "error": "Requested appointment slot is no longer available."
            })

        appointment = AppointmentCreate(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_date=selected_date,
            appointment_time=selected_time
        )

        created = appointment_service.create_appointment(
            appointment,
            int(user_id),
            session
        )

        return json.dumps({
            "success": True,
            "message": "Appointment booked successfully.",
            "appointment_id": created.id,
            "patient_name": patient.name,
            "doctor_name": doctor.name,
            "specialization": doctor.specialization,
            "appointment_date": created.appointment_date,
            "appointment_time": created.appointment_time
        })    

@mcp.tool(name="get_current_patient")
def get_current_patient() -> str:
    """Get the authenticated patient's profile for the current AI request."""

    user_id = os.getenv("ODASHA_USER_ID")

    if not user_id:
        return json.dumps({
            "error": "Authenticated user context is missing"
        })

    with Session(engine) as session:

        patient = session.exec(
            select(Patient).where(
                Patient.user_id == int(user_id)
            )
        ).first()

        if not patient:
            return json.dumps({
                "error": "Patient profile not found"
            })

        return json.dumps({
            "id": patient.id,
            "name": patient.name,
            "age": patient.age,
            "gender": patient.gender
        })

@mcp.tool(name="prepare_appointment")
def prepare_appointment(
    doctor_id: int,
    appointment_date: str,
    appointment_time: str
) -> str:
    """Validate an appointment request for the authenticated patient without booking it."""

    user_id = os.getenv("ODASHA_USER_ID")

    if not user_id:
        return json.dumps({
            "error": "Authenticated user context is missing"
        })

    try:
        selected_date = date.fromisoformat(appointment_date)
    except ValueError:
        return json.dumps({
            "error": "Invalid date. Use YYYY-MM-DD format."
        })

    with Session(engine) as session:

        patient = session.exec(
            select(Patient).where(
                Patient.user_id == int(user_id)
            )
        ).first()

        if not patient:
            return json.dumps({
                "error": "Patient profile not found"
            })

        doctor = session.get(Doctor, doctor_id)

        if not doctor:
            return json.dumps({
                "error": "Doctor not found"
            })

        slots = appointment_service.get_available_slots(
            doctor_id,
            selected_date,
            session
        )

        requested_slot = next(
            (
                slot
                for slot in slots
                if slot["time"] == appointment_time
            ),
            None
        )

        if not requested_slot:
            return json.dumps({
                "error": "Requested appointment time is not a valid slot."
            })

        if not requested_slot["available"]:
            return json.dumps({
                "error": "Requested appointment slot is already booked or unavailable."
            })

        return json.dumps({
            "ready_for_confirmation": True,
            "patient_id": patient.id,
            "patient_name": patient.name,
            "doctor_id": doctor.id,
            "doctor_name": doctor.name,
            "specialization": doctor.specialization,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time
        })
    
@mcp.tool(name="find_doctor")
def find_doctor(doctor_name: str) -> str:
    """Find a doctor by name and return the doctor's ID, name, and specialization."""

    try:

        with Session(engine) as session:

            doctors = doctor_service.get_doctors(session)

            search_name = doctor_name.lower().strip()

            results = []

            for doctor in doctors:

                if search_name in doctor.name.lower():

                    results.append({
                        "id": doctor.id,
                        "name": doctor.name,
                        "specialization": doctor.specialization
                    })

            if not results:

                return json.dumps({
                    "message": "Doctor not found"
                })

            return json.dumps(results)

    except Exception as error:

        return json.dumps({
            "error": str(error)
        })
    
@mcp.tool(name="get_available_slots")
def get_available_slots(
    doctor_id: int,
    appointment_date: str
) -> str:
    """Get available appointment time slots for a doctor on a specific date."""

    try:
        if "-" in appointment_date and len(appointment_date) == 10:
            selected_date = date.fromisoformat(appointment_date)

        else:
            selected_date = datetime.strptime(
                appointment_date,
                "%d %B %Y"
            ).date()

    except ValueError:
        return (
            "Invalid appointment date. "
            "Please provide the date in YYYY-MM-DD format."
        )

    with Session(engine) as session:

        slots = appointment_service.get_available_slots(
            doctor_id,
            selected_date,
            session
        )

        return json.dumps(slots)
    
@mcp.tool(name="search_healthcare_knowledge")
def search_healthcare_knowledge(question: str) -> list[str]:
    """Search the healthcare knowledge base for information relevant to a question."""

    return retrieve_chunks(question)

@mcp.tool(name="search_doctors")
def search_doctors(specialization: str) -> list[dict]:
    """Find doctors by medical specialization."""

    return _search_doctors(specialization)