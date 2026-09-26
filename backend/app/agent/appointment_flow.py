import json
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from app.mcp.tools import (
    find_doctor,
    get_available_slots,
    prepare_appointment,
    book_appointment
)


class AppointmentState(TypedDict):

    user_id: int

    doctor_name: str | None
    doctor_id: int | None

    appointment_date: str | None
    appointment_time: str | None

    confirmed: bool

    response: str | None


def find_doctor_node(state: AppointmentState):

    doctor_name = state["doctor_name"]

    if not doctor_name:
        return {
            "response": "Doctor name is required."
        }

    result = find_doctor(doctor_name)

    data = json.loads(result)

    if isinstance(data, dict) and data.get("error"):
        return {
            "response": data["error"]
        }

    if not data:
        return {
            "response": "Doctor not found."
        }

    doctor = data[0]

    return {
        "doctor_id": doctor["id"],
        "doctor_name": doctor["name"],
        "response": f"Doctor found: {doctor['name']}"
    }


def check_availability_node(state: AppointmentState):

    doctor_id = state["doctor_id"]
    appointment_date = state["appointment_date"]
    appointment_time = state["appointment_time"]

    if not doctor_id:
        return {
            "response": "Doctor must be identified first."
        }

    if not appointment_date or not appointment_time:
        return {
            "response": "Appointment date and time are required."
        }

    result = get_available_slots(
        doctor_id,
        appointment_date
    )

    slots = json.loads(result)

    requested_slot = next(
        (
            slot
            for slot in slots
            if slot["time"] == appointment_time
        ),
        None
    )

    if not requested_slot:
        return {
            "response": "The requested time is not a valid appointment slot."
        }

    if not requested_slot["available"]:
        return {
            "response": (
                f"{appointment_time} is not available "
                f"on {appointment_date}."
            )
        }

    return {
        "response": (
            f"{appointment_time} is available "
            f"on {appointment_date}."
        )
    }


def prepare_appointment_node(state: AppointmentState):

    doctor_id = state["doctor_id"]
    appointment_date = state["appointment_date"]
    appointment_time = state["appointment_time"]

    if not doctor_id:
        return {
            "response": "Doctor must be identified first."
        }

    if not appointment_date or not appointment_time:
        return {
            "response": "Appointment date and time are required."
        }

    result = prepare_appointment(
        doctor_id,
        appointment_date,
        appointment_time
    )

    data = json.loads(result)

    if data.get("error"):
        return {
            "response": data["error"],
            "confirmed": False
        }

    return {
        "pending_booking": data,
        "confirmed": False,
        "response": (
            f"Your appointment with "
            f"{data['doctor_name']} ({data['specialization']}) "
            f"on {data['appointment_date']} at "
            f"{data['appointment_time']} is ready for confirmation."
        )
    }


def book_appointment_node(state: AppointmentState):

    if not state["confirmed"]:
        return {
            "response": "Appointment confirmation is required before booking."
        }

    pending_booking = state.get("pending_booking")

    if not pending_booking:
        return {
            "response": "There is no appointment waiting for confirmation."
        }

    result = book_appointment(
        pending_booking["doctor_id"],
        pending_booking["appointment_date"],
        pending_booking["appointment_time"],
        "CONFIRM"
    )

    data = json.loads(result)

    if data.get("error"):
        return {
            "response": data["error"]
        }

    return {
        "response": (
            f"Appointment booked successfully with "
            f"{data['doctor_name']} on "
            f"{data['appointment_date']} at "
            f"{data['appointment_time']}."
        )
    }

builder = StateGraph(AppointmentState)


builder.add_node(
    "find_doctor",
    find_doctor_node
)

builder.add_node(
    "check_availability",
    check_availability_node
)

builder.add_node(
    "prepare_appointment",
    prepare_appointment_node
)


builder.add_edge(
    START,
    "find_doctor"
)

builder.add_edge(
    "find_doctor",
    "check_availability"
)

builder.add_edge(
    "check_availability",
    "prepare_appointment"
)

builder.add_edge(
    "prepare_appointment",
    END
)


appointment_graph = builder.compile()