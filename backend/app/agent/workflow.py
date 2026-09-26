from langgraph.graph import StateGraph, START, END
from app.agent.graph import run_agent
from app.agent.state import AgentState


def classify_intent(state: AgentState):
    """
    Decide which part of the healthcare assistant should handle the request.
    """

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

    return {
        "intent": intent
    }


async def healthcare_node(state: AgentState):

    question = state["messages"][-1].content
    user_id = state["user_id"]

    answer = await run_agent(
        question,
        user_id
    )

    return {
        "response": answer
    }


async def doctor_node(state: AgentState):

    question = state["messages"][-1].content
    user_id = state["user_id"]

    answer = await run_agent(
        question,
        user_id
    )

    return {
        "response": answer
    }


async def appointment_node(state: AgentState):

    question = state["messages"][-1].content
    user_id = state["user_id"]

    answer = await run_agent(
        question,
        user_id
    )

    return {
        "response": answer
    }


def route_intent(state: AgentState):

    return state["intent"]


builder = StateGraph(AgentState)

builder.add_node(
    "classify_intent",
    classify_intent
)

builder.add_node(
    "healthcare",
    healthcare_node
)

builder.add_node(
    "doctor",
    doctor_node
)

builder.add_node(
    "appointment",
    appointment_node
)

builder.add_edge(
    START,
    "classify_intent"
)

builder.add_conditional_edges(
    "classify_intent",
    route_intent,
    {
        "healthcare": "healthcare",
        "doctor": "doctor",
        "appointment": "appointment"
    }
)

builder.add_edge(
    "healthcare",
    END
)

builder.add_edge(
    "doctor",
    END
)

builder.add_edge(
    "appointment",
    END
)


healthcare_graph = builder.compile()