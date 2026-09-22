from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database.session import get_session
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse
)
from app.auth.dependencies import get_current_user , require_role
from app.models.user import User

from app.services import appointment_service
from datetime import date

router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


@router.post("/")
def create_appointment(
    appointment: AppointmentCreate,
    current_user: User = Depends(
        require_role(["patient"])
    ),
    session: Session = Depends(get_session)
):
    return appointment_service.create_appointment(
        appointment,
        current_user.id,
        session
    )


@router.get("/", response_model=list[AppointmentResponse])
def get_appointments(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return appointment_service.get_appointments(
        session
    )


@router.get("/patient/{patient_id}", response_model=list[AppointmentResponse])
def get_patient_appointments(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return appointment_service.get_patient_appointments(
        patient_id,
        session
    )


@router.get("/doctor/{doctor_id}", response_model=list[AppointmentResponse])
def get_doctor_appointments(
    doctor_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return appointment_service.get_doctor_appointments(
        doctor_id,
        session
    )
@router.get("/available-slots/{doctor_id}")
def get_available_slots(
    doctor_id: int,
    appointment_date: date,
    session: Session = Depends(get_session)
):
    return appointment_service.get_available_slots(
        doctor_id,
        appointment_date,
        session
    )

@router.get("/my", response_model=list[AppointmentResponse])
def get_my_patient_appointments (
    current_user: User = Depends(
        require_role(["patient"])
    ),
    session: Session = Depends(get_session)
):
    return appointment_service.get_my_patient_appointments(
        current_user.id,
        session
    )
    
@router.get("/my-doctor", response_model=list[AppointmentResponse])

def get_my_doctor_appointments(
    current_user: User = Depends(
        require_role(["doctor"])
    ),
    session: Session = Depends(get_session)
):
    return appointment_service.get_my_doctor_appointments(
        current_user.id,
        session
    )

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    return appointment_service.get_appointment(
        appointment_id,
        session
    )


@router.put("/{appointment_id}")
def update_appointment(
    appointment_id: int,
    updated_appointment: AppointmentUpdate,
    current_user: User = Depends(
        require_role(["admin"])
    ),  
    session: Session = Depends(get_session)
):
    return appointment_service.update_appointment(
        appointment_id,
        updated_appointment,
        session
    )


@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    current_user: User = Depends(
        require_role(["admin"])
    ),
    session: Session = Depends(get_session)
):
    return appointment_service.delete_appointment(
        appointment_id,
        session
    )