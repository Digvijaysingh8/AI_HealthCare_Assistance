from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.database.session import get_session
from app.schemas.auth import RegisterRequest, LoginRequest
from app.auth.dependencies import require_role
from app.services.auth_service import (
    register_user,
    login_user
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(
    user_data: RegisterRequest,
    session: Session = Depends(get_session)
):
    return register_user(
        user_data,
        session
    )


@router.post("/login")
def login(
    user_data: LoginRequest,
    session: Session = Depends(get_session)
):
    return login_user(
        user_data,
        session
    )

@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }
@router.get("/patient-only")
def patient_only(
    current_user: User = Depends(
        require_role(["patient"])
    )
):
    return {
        "message": "You are a patient",
        "email": current_user.email
    }

@router.get("/doctor-only")
def doctor_only(
    current_user: User = Depends(
        require_role(["doctor"])
    )
):
    return {
        "message": "You are a doctor",
        "email": current_user.email
    }