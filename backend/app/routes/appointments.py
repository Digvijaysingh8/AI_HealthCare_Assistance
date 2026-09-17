from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database.session import get_session
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse
)

from app.services import appointment_service


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


@router.post("/")
def create_appointment(
    appointment: AppointmentCreate,
    session: Session = Depends(get_session)
):
    return appointment_service.create_appointment(
        appointment,
        session
    )


@router.get("/", response_model=list[AppointmentResponse])
def get_appointments(
    session: Session = Depends(get_session)
):
    return appointment_service.get_appointments(
        session
    )


@router.get("/patient/{patient_id}", response_model=list[AppointmentResponse])
def get_patient_appointments(
    patient_id: int,
    session: Session = Depends(get_session)
):
    return appointment_service.get_patient_appointments(
        patient_id,
        session
    )


@router.get("/doctor/{doctor_id}", response_model=list[AppointmentResponse])
def get_doctor_appointments(
    doctor_id: int,
    session: Session = Depends(get_session)
):
    return appointment_service.get_doctor_appointments(
        doctor_id,
        session
    )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
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
    session: Session = Depends(get_session)
):
    return appointment_service.delete_appointment(
        appointment_id,
        session
    )