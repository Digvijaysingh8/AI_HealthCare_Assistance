import asyncio
import logging
import os

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.ai import AIRequest, AIResponse
from app.ai.ai_service import ask_healthcare_assistant
from app.auth.dependencies import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/ai",
    tags=["AI Assistant"]
)

# A cold call spawns an MCP subprocess and calls the model, so it is slow.
# Bounding it here means an over-long request fails with a readable 504 that
# carries CORS headers, instead of being cut off further out where the client
# only sees an opaque gateway failure.
REQUEST_TIMEOUT_SECONDS = float(
    os.getenv("AI_REQUEST_TIMEOUT_SECONDS", "55")
)


@router.post("/chat", response_model=AIResponse)
async def chat(
    request: AIRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        result = await asyncio.wait_for(
            ask_healthcare_assistant(
                question=request.question,
                user_id=current_user.id,
                thread_id=request.thread_id,
                confirmed=request.confirmed
            ),
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.warning(
            "ai/chat timed out after %ss for user %s",
            REQUEST_TIMEOUT_SECONDS,
            current_user.id,
        )
        raise HTTPException(
            status_code=504,
            detail=(
                "The assistant took too long to respond and was stopped. "
                "This usually means the server is starting up or busy. "
                "Please try again."
            )
        )
    except MemoryError:
        # Surface the real cause; the default 500 body hides it.
        logger.exception("ai/chat ran out of memory")
        raise HTTPException(
            status_code=503,
            detail=(
                "The assistant ran out of memory handling that question. "
                "Please try again in a moment."
            )
        )
    except Exception:
        # Log the traceback server-side, return something a user can read.
        logger.exception("ai/chat failed for user %s", current_user.id)
        raise HTTPException(
            status_code=500,
            detail=(
                "The assistant could not answer that question. "
                "Please try rephrasing it."
            )
        )

    return AIResponse(**result)