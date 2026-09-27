from pydantic import BaseModel


class AIRequest(BaseModel):
    question: str
    thread_id: str | None = None
    confirmed: bool = False


class AIResponse(BaseModel):
    answer: str
    thread_id: str | None = None
    requires_confirmation: bool = False
    pending_booking: dict | None = None