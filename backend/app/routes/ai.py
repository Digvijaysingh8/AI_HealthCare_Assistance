from fastapi import APIRouter

from app.schemas.ai import AIRequest, AIResponse
from app.ai.ai_service import ask_healthcare_assistant


router = APIRouter(
    prefix="/ai",
    tags=["AI Assistant"]
)


@router.post("/chat", response_model=AIResponse)
def chat(request: AIRequest):

    answer = ask_healthcare_assistant(
        request.question
    )

    return AIResponse(
        answer=answer
    )