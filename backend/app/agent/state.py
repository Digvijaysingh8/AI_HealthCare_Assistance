from langgraph.graph import MessagesState


class AgentState(MessagesState):
    user_id: int
    intent: str | None
    response: str | None
    pending_booking: dict | None
    thread_id: str | None
    requires_confirmation: bool