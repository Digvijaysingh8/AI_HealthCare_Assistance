from mcp.server.mcpserver import MCPServer
from sqlmodel import Session
from app.rag.retriever import retrieve_chunks
from app.database.database import engine
from app.services import doctor_service
from datetime import date , datetime
from app.services import appointment_service
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