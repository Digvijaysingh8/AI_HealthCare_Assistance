from fastapi import APIRouter, Depends

from app.schemas.ai import AIRequest, AIResponse
from app.ai.ai_service import ask_healthcare_assistant
from app.auth.dependencies import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/ai",
    tags=["AI Assistant"]
)


@router.post("/chat", response_model=AIResponse)
async def chat(
    request: AIRequest,
    current_user: User = Depends(get_current_user)
):

    answer = await ask_healthcare_assistant(
        request.question,
        current_user.id
    )

    return AIResponse(
        answer=answer
    )