from app.agent.workflow import healthcare_graph
from app.agent.appointment_flow import appointment_graph
from langgraph.types import Command


async def ask_healthcare_assistant(
    question: str,
    user_id: int,
    thread_id: str | None = None,
    confirmed: bool = False
):
    # Resume the paused appointment when the user confirms.
    if confirmed:
        if not thread_id:
            return {
                "answer": "No pending appointment was found.",
                "thread_id": None,
                "requires_confirmation": False,
                "pending_booking": None
            }

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        checkpoint = await appointment_graph.aget_state(config)
        saved_state = checkpoint.values

        # Verify that this appointment belongs to the logged-in user.
        if (
            not saved_state
            or saved_state.get("user_id") != user_id
            or saved_state.get("status") != "ready_for_confirmation"
        ):
            return {
                "answer": "No valid pending appointment was found.",
                "thread_id": None,
                "requires_confirmation": False,
                "pending_booking": None
            }

        result = await appointment_graph.ainvoke(
            Command(resume=True),
            config=config
        )

        return {
            "answer": result.get(
                "response",
                "Appointment processing completed."
            ),
            "thread_id": thread_id,
            "requires_confirmation": False,
            "pending_booking": None
        }

    # Process a new request through the main workflow.
    result = await healthcare_graph.ainvoke({
        "messages": [
            {"role": "user", "content": question}
        ],
        "user_id": user_id,
        "intent": None,
        "response": None,
        "pending_booking": None,
        "thread_id": thread_id,
        "requires_confirmation": False
    })

    return {
        "answer": result.get("response", ""),
        "thread_id": result.get("thread_id"),
        "requires_confirmation": result.get(
            "requires_confirmation", False
        ),
        "pending_booking": result.get("pending_booking")
    }