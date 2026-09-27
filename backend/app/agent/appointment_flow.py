
import json
from datetime import date, datetime
from typing import TypedDict

from fastapi import HTTPException
from sqlmodel import Session, select

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt

from app.database.database import engine
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.user import User
from app.schemas.appointment import AppointmentCreate
from app.services import doctor_service, appointment_service


class AppointmentState(TypedDict, total=False):
    user_id: int
    doctor_name: str
    doctor_id: int
    appointment_date: str
    appointment_time: str
    confirmed: bool
    pending_booking: dict
    response: str
    status: str
    appointment_id: int


def find_doctor_node(state: AppointmentState):

    doctor_name = state.get("doctor_name", "").strip()

    if not doctor_name:
        return {
            "status": "error",
            "response": "Doctor name is required."
        }

    search_name = doctor_name.casefold().replace("dr.", "").strip()

    with Session(engine) as session:
        doctors = doctor_service.get_doctors(session)

        matches = [
            doctor for doctor in doctors
            if search_name in
            doctor.name.casefold().replace("dr.", "").strip()
        ]

        if not matches:
            return {
                "status": "error",
                "response": "Doctor not found."
            }

        if len(matches) > 1:
            return {
                "status": "error",
                "response": (
                    "Multiple doctors found. "
                    "Please specify the doctor's full name."
                )
            }

        doctor = matches[0]

        return {
            "status": "ok",
            "doctor_id": doctor.id,
            "doctor_name": doctor.name,
            "response": f"Doctor found: {doctor.name}"
        }


def check_availability_node(state: AppointmentState):

    doctor_id = state.get("doctor_id")
    appointment_date = state.get("appointment_date")
    appointment_time = state.get("appointment_time")

    if not doctor_id:
        return {
            "status": "error",
            "response": "Doctor must be identified first."
        }

    try:
        selected_date = date.fromisoformat(appointment_date)
        selected_time = datetime.strptime(
            appointment_time, "%H:%M"
        ).strftime("%H:%M")
    except (ValueError, TypeError):
        return {
            "status": "error",
            "response": "Invalid date or time. Use YYYY-MM-DD and HH:MM."
        }

    if selected_date < date.today():
        return {
            "status": "unavailable",
            "response": "Appointment date cannot be in the past."
        }

    with Session(engine) as session:
        slots = appointment_service.get_available_slots(
            doctor_id,
            selected_date,
            session
        )

    requested_slot = next(
        (slot for slot in slots if slot["time"] == selected_time),
        None
    )

    if not requested_slot:
        return {
            "status": "unavailable",
            "response": "The requested time is not a valid appointment slot."
        }

    if not requested_slot["available"]:
        return {
            "status": "unavailable",
            "response": (
                f"{selected_time} is not available "
                f"on {selected_date.isoformat()}."
            )
        }

    return {
        "status": "available",
        "response": (
            f"{selected_time} is available "
            f"on {selected_date.isoformat()}."
        )
    }


def prepare_appointment_node(state: AppointmentState):

    user_id = state.get("user_id")
    doctor_id = state.get("doctor_id")
    appointment_date = state.get("appointment_date")
    appointment_time = state.get("appointment_time")

    if not user_id:
        return {
            "status": "error",
            "response": "Authenticated user context is missing."
        }

    try:
        selected_date = date.fromisoformat(appointment_date)
        selected_time = datetime.strptime(
            appointment_time, "%H:%M"
        ).strftime("%H:%M")
    except (ValueError, TypeError):
        return {
            "status": "error",
            "response": "Invalid appointment date or time."
        }

    with Session(engine) as session:
        user = session.get(User, user_id)

        if not user or user.role != "patient":
            return {
                "status": "error",
                "response": "Only authenticated patients can book appointments."
            }

        patient = session.exec(
            select(Patient).where(Patient.user_id == user_id)
        ).first()

        if not patient:
            return {
                "status": "error",
                "response": "Patient profile not found."
            }

        doctor = session.get(Doctor, doctor_id)

        if not doctor:
            return {
                "status": "error",
                "response": "Doctor not found."
            }

        # Recheck availability immediately before preparing.
        slots = appointment_service.get_available_slots(
            doctor_id,
            selected_date,
            session
        )

        requested_slot = next(
            (slot for slot in slots if slot["time"] == selected_time),
            None
        )

        if not requested_slot or not requested_slot["available"]:
            return {
                "status": "unavailable",
                "response": "This appointment slot is no longer available."
            }

        booking = {
            "patient_id": patient.id,
            "patient_name": patient.name,
            "doctor_id": doctor.id,
            "doctor_name": doctor.name,
            "specialization": doctor.specialization,
            "appointment_date": selected_date.isoformat(),
            "appointment_time": selected_time
        }

    return {
        "status": "ready_for_confirmation",
        "pending_booking": booking,
        "confirmed": False,
        "response": (
            f"Your appointment with {booking['doctor_name']} "
            f"({booking['specialization']}) on "
            f"{booking['appointment_date']} at "
            f"{booking['appointment_time']} is ready for confirmation."
        )
    }


def confirmation_node(state: AppointmentState):

    booking = state.get("pending_booking")

    if not booking:
        return {
            "status": "error",
            "confirmed": False,
            "response": "No appointment is waiting for confirmation."
        }

    # Pause the graph and wait for explicit human approval.
    approval = interrupt({
        "type": "appointment_confirmation",
        "message": "Do you confirm this appointment?",
        "booking": {
            "doctor_name": booking["doctor_name"],
            "appointment_date": booking["appointment_date"],
            "appointment_time": booking["appointment_time"]
        }
    })

    confirmed = (
        approval is True
        or (
            isinstance(approval, dict)
            and approval.get("confirmed") is True
        )
    )

    if confirmed:
        return {
            "status": "confirmed",
            "confirmed": True,
            "response": "Appointment confirmed. Proceeding with booking."
        }

    return {
        "status": "cancelled",
        "confirmed": False,
        "response": "Appointment was not confirmed. No booking was made."
    }


def book_appointment_node(state: AppointmentState):

    if state.get("confirmed") is not True:
        return {
            "status": "error",
            "response": "Appointment confirmation is required before booking."
        }

    booking = state.get("pending_booking")
    user_id = state.get("user_id")

    if not booking or not user_id:
        return {
            "status": "error",
            "response": "Booking details or authenticated user are missing."
        }

    try:
        selected_date = date.fromisoformat(
            booking["appointment_date"]
        )
        selected_time = datetime.strptime(
            booking["appointment_time"], "%H:%M"
        ).time()

        with Session(engine) as session:
            user = session.get(User, user_id)

            if not user or user.role != "patient":
                return {
                    "status": "error",
                    "response": "Only authenticated patients can book appointments."
                }

            patient = session.exec(
                select(Patient).where(Patient.user_id == user_id)
            ).first()

            if (
                not patient
                or patient.id != booking["patient_id"]
            ):
                return {
                    "status": "error",
                    "response": "Patient ownership could not be verified."
                }

            # Check that the slot is still available.
            slots = appointment_service.get_available_slots(
                booking["doctor_id"],
                selected_date,
                session
            )

            requested_slot = next(
                (
                    slot for slot in slots
                    if slot["time"] == booking["appointment_time"]
                ),
                None
            )

            if not requested_slot or not requested_slot["available"]:
                return {
                    "status": "unavailable",
                    "response": "This appointment slot is no longer available."
                }

            appointment = AppointmentCreate(
                patient_id=patient.id,
                doctor_id=booking["doctor_id"],
                appointment_date=selected_date,
                appointment_time=selected_time
            )

            created = appointment_service.create_appointment(
                appointment,
                user_id,
                session
            )

            return {
                "status": "booked",
                "response": (
                    f"Appointment booked successfully with "
                    f"{booking['doctor_name']} on "
                    f"{created.appointment_date} at "
                    f"{created.appointment_time}. "
                    f"Appointment ID: {created.id}."
                ),
                "appointment_id": created.id
            }

    except HTTPException as exc:
        return {
            "status": "error",
            "response": str(exc.detail)
        }


def route_after_doctor(state: AppointmentState):
    if state.get("status") == "ok":
        return "check_availability"
    return "end"


def route_after_availability(state: AppointmentState):
    if state.get("status") == "available":
        return "prepare_appointment"
    return "end"


def route_after_preparation(state: AppointmentState):
    if state.get("status") == "ready_for_confirmation":
        return "confirmation"
    return "end"


def route_after_confirmation(state: AppointmentState):
    if state.get("confirmed") is True:
        return "book"
    return "end"


builder = StateGraph(AppointmentState)

builder.add_node("find_doctor", find_doctor_node)
builder.add_node("check_availability", check_availability_node)
builder.add_node("prepare_appointment", prepare_appointment_node)
builder.add_node("confirmation", confirmation_node)
builder.add_node("book_appointment", book_appointment_node)

builder.add_edge(START, "find_doctor")

builder.add_conditional_edges(
    "find_doctor",
    route_after_doctor,
    {
        "check_availability": "check_availability",
        "end": END
    }
)

builder.add_conditional_edges(
    "check_availability",
    route_after_availability,
    {
        "prepare_appointment": "prepare_appointment",
        "end": END
    }
)

builder.add_conditional_edges(
    "prepare_appointment",
    route_after_preparation,
    {
        "confirmation": "confirmation",
        "end": END
    }
)

builder.add_conditional_edges(
    "confirmation",
    route_after_confirmation,
    {
        "book": "book_appointment",
        "end": END
    }
)

builder.add_edge("book_appointment", END)

checkpointer = InMemorySaver()

appointment_graph = builder.compile(
    checkpointer=checkpointer
)