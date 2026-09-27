import os
import uuid
from datetime import date
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq

from app.agent.graph import run_agent
from app.agent.state import AgentState
from app.agent.appointment_flow import appointment_graph


class AppointmentDetails(BaseModel):
    doctor_name: str | None = Field(
        default=None,
        description="The requested doctor's name"
    )
    appointment_date: str | None = Field(
        default=None,
        description="Appointment date in YYYY-MM-DD format"
    )
    appointment_time: str | None = Field(
        default=None,
        description="Appointment time in HH:MM 24-hour format"
    )


def classify_intent(state: AgentState):
    question = state["messages"][-1].content.lower()

    if any(
        word in question
        for word in [
            "book",
            "appointment",
            "slot",
            "schedule",
            "confirm"
        ]
    ):
        intent = "appointment"

    elif any(
        word in question
        for word in [
            "doctor",
            "specialist",
            "physician",
            "cardiologist",
            "dermatologist",
            "neurologist"
        ]
    ):
        intent = "doctor"

    else:
        intent = "healthcare"

    return {"intent": intent}


async def healthcare_node(state: AgentState):
    question = state["messages"][-1].content
    answer = await run_agent(question, state["user_id"])

    return {"response": answer}


async def doctor_node(state: AgentState):
    question = state["messages"][-1].content
    answer = await run_agent(question, state["user_id"])

    return {"response": answer}


async def appointment_node(state: AgentState):
    question = state["messages"][-1].content
    user_id = state["user_id"]

    # Availability-only questions continue using the existing agent.
    booking_keywords = ["book", "reserve", "schedule"]
    is_booking = any(
        word in question.lower()
        for word in booking_keywords
    )

    if not is_booking:
        answer = await run_agent(question, user_id)
        return {
            "response": answer,
            "requires_confirmation": False
        }

    # Extract booking details from the user's request.
    model = ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=os.getenv("GROQ_API_KEY")
    )

    extractor = model.with_structured_output(AppointmentDetails)

    details = await extractor.ainvoke(
        f"""
        Extract the appointment details from this request.

        Today's date is {date.today().isoformat()}.
        Convert relative dates using today's date.
        Return the date in YYYY-MM-DD format.
        Return the time in 24-hour HH:MM format.
        If a detail is missing or unclear, return null for it.
        Do not invent any details.

        User request:
        {question}
        """
    )

    # Ask the user for any missing information.
    missing = []

    if not details.doctor_name:
        missing.append("doctor's name")

    if not details.appointment_date:
        missing.append("appointment date")

    if not details.appointment_time:
        missing.append("appointment time")

    if missing:
        return {
            "response": (
                "Please provide the following details to proceed: "
                + ", ".join(missing)
                + "."
            ),
            "requires_confirmation": False
        }

    # Each appointment conversation gets its own checkpoint thread.
    thread_id = state.get("thread_id") or str(uuid.uuid4())

    appointment_state = {
        "user_id": user_id,
        "doctor_name": details.doctor_name,
        "doctor_id": None,
        "appointment_date": details.appointment_date,
        "appointment_time": details.appointment_time,
        "confirmed": False,
        "pending_booking": None,
        "response": None,
        "status": None
    }

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = await appointment_graph.ainvoke(
        appointment_state,
        config=config
    )

    interrupted = bool(result.get("__interrupt__"))

    response = result.get("response")

    if result.get("status") == "ready_for_confirmation":
        booking = result.get("pending_booking") or {}

        response = (
            "Please review your appointment details:\n"
            f"Doctor: {booking.get('doctor_name')}\n"
            f"Date: {booking.get('appointment_date')}\n"
            f"Time: {booking.get('appointment_time')}\n\n"
            "Please confirm to proceed with booking."
        )

    return {
        "response": response or "Appointment processing completed.",
        "thread_id": thread_id,
        "pending_booking": result.get("pending_booking"),
        "requires_confirmation": interrupted
    }


def route_intent(state: AgentState):
    return state["intent"]


builder = StateGraph(AgentState)

builder.add_node("classify_intent", classify_intent)
builder.add_node("healthcare", healthcare_node)
builder.add_node("doctor", doctor_node)
builder.add_node("appointment", appointment_node)

builder.add_edge(START, "classify_intent")

builder.add_conditional_edges(
    "classify_intent",
    route_intent,
    {
        "healthcare": "healthcare",
        "doctor": "doctor",
        "appointment": "appointment"
    }
)

builder.add_edge("healthcare", END)
builder.add_edge("doctor", END)
builder.add_edge("appointment", END)

healthcare_graph = builder.compile()