from fastapi import APIRouter, Depends,HTTPException
from sqlmodel import Session, select
from datetime import date 

from app.models.appointment import Appointment
from app.database.session import get_session
from app.schemas.appointment import AppointmentCreate , AppointmentUpdate
from app.models.patient import Patient
from app.models.doctor import Doctor





router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)

@router.post("/")
def create_appointment(
    appointment: AppointmentCreate,
    session: Session = Depends(get_session)
):
    patient = session.get(Patient, appointment.patient_id)

    if not patient:
     raise HTTPException(
        status_code=404,
        detail="Patient not found"
    )

    doctor = session.get(Doctor, appointment.doctor_id)

    if not  doctor:
      raise HTTPException(
        status_code=404,
        detail="Doctor not found"
    )
    appointment_date = appointment.appointment_date

    if appointment_date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Appointment date cannot be in the past"
        )

    new_appointment = Appointment(
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        appointment_date=appointment.appointment_date.isoformat(),
        appointment_time=appointment.appointment_time.strftime("%H:%M")
    )

    session.add(new_appointment)
    session.commit()
    session.refresh(new_appointment)

    return new_appointment


@router.get("/")
def get_appointments(
    session: Session = Depends(get_session)
):
    appointments = session.exec(
        select(Appointment)
    ).all()

    return appointments


@router.get("/{appointment_id}")
def get_appointment(
    appointment_id: int,
    session: Session = Depends(get_session)
):
    appointment = session.get(Appointment, appointment_id)
    return appointment


@router.put("/{appointment_id}")
def update_appointment(
    appointment_id: int,
    updated_appointment: AppointmentUpdate,
    session: Session = Depends(get_session)
):
    appointment = session.get(Appointment, appointment_id)

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    patient = session.get(Patient, updated_appointment.patient_id)

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    doctor = session.get(Doctor, updated_appointment.doctor_id)

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )
    appointment_date = updated_appointment.appointment_date

    if appointment_date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Appointment date cannot be in the past"
        )

 

    appointment.patient_id = updated_appointment.patient_id
    appointment.doctor_id = updated_appointment.doctor_id
    appointment.appointment_date = updated_appointment.appointment_date.isoformat()
    appointment.appointment_time = updated_appointment.appointment_time.strftime("%H:%M")

    session.add(appointment)
    session.commit()
    session.refresh(appointment)

    return appointment


@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    session: Session = Depends(get_session)
):
    appointment = session.get(Appointment, appointment_id)

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    session.delete(appointment)
    session.commit()

    return {"message": "Appointment deleted successfully"}