from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor

from app.schemas.auth import RegisterRequest, LoginRequest

from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token


def register_user(
    user_data: RegisterRequest,
    session: Session
):
    if user_data.role not in [
        "patient",
        "doctor",
        "admin"
    ]:
        raise HTTPException(
            status_code=400,
            detail="Invalid role"
        )

    existing_user = session.exec(
        select(User).where(
            User.email == user_data.email
        )
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        email=user_data.email,
        password_hash=hash_password(
            user_data.password
        ),
        role=user_data.role
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Create profile based on role
    if user_data.role == "patient":

        patient = Patient(
            user_id=new_user.id,
            name=user_data.email.split("@")[0],
            age=0,
            gender="Not specified"
        )

        session.add(patient)

    elif user_data.role == "doctor":

        doctor = Doctor(
            user_id=new_user.id,
            name=user_data.email.split("@")[0],
            specialization="Not specified"
        )

        session.add(doctor)

    session.commit()

    return {
        "id": new_user.id,
        "email": new_user.email,
        "role": new_user.role
    }


def login_user(
    user_data: LoginRequest,
    session: Session
):
    user = session.exec(
        select(User).where(
            User.email == user_data.email
        )
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_valid = verify_password(
        user_data.password,
        user.password_hash
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role
    })

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id": user.id,
        "email": user.email,
        "role": user.role
    }