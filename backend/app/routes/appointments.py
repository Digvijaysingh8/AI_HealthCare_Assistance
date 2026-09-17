from fastapi import APIRouter, Depends,HTTPException
from sqlmodel import Session, select
from datetime import date 

from app.models.appointment import Appointment
from app.database.session import get_session
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse
)
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
    existing_appointment = session.exec(
    select(Appointment).where(
        Appointment.doctor_id == appointment.doctor_id,
        Appointment.appointment_date == appointment.appointment_date.isoformat(),
        Appointment.appointment_time == appointment.appointment_time.strftime("%H:%M")
    )
    ).first()

    if existing_appointment:
        raise HTTPException(
            status_code=400,
            detail="Doctor already has an appointment at this date and time"
        )
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


@router.get("/", response_model=list[AppointmentResponse])
def get_appointments(
    session: Session = Depends(get_session)
):
    statement = (
    select(Appointment, Patient, Doctor)
    .join(Patient, Appointment.patient_id == Patient.id)
    .join(Doctor, Appointment.doctor_id == Doctor.id)
    .order_by(
        Appointment.appointment_date,
        Appointment.appointment_time
     )
    )

    results = session.exec(statement).all()

    response = []

    for appointment, patient, doctor in results:
        response.append({
            "id": appointment.id,
            "patient_id": appointment.patient_id,
            "patient_name": patient.name,
            "doctor_id": appointment.doctor_id,
            "doctor_name": doctor.name,
            "appointment_date": appointment.appointment_date,
            "appointment_time": appointment.appointment_time
        })

    return response
@router.get("/patient/{patient_id}", response_model=list[AppointmentResponse])
def get_patient_appointments(
    patient_id: int,
    session: Session = Depends(get_session)
):
    patient = session.get(Patient, patient_id)

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    statement = (
        select(Appointment, Patient, Doctor)
        .join(Patient, Appointment.patient_id == Patient.id)
        .join(Doctor, Appointment.doctor_id == Doctor.id)
        .where(Appointment.patient_id == patient_id)
        .order_by(
            Appointment.appointment_date,
            Appointment.appointment_time
        )
    )

    results = session.exec(statement).all()

    response = []

    for appointment, patient, doctor in results:
        response.append({
            "id": appointment.id,
            "patient_id": appointment.patient_id,
            "patient_name": patient.name,
            "doctor_id": appointment.doctor_id,
            "doctor_name": doctor.name,
            "appointment_date": appointment.appointment_date,
            "appointment_time": appointment.appointment_time
        })

    return response
@router.get("/doctor/{doctor_id}", response_model=list[AppointmentResponse])
def get_doctor_appointments(
    doctor_id: int,
    session: Session = Depends(get_session)
):
    doctor = session.get(Doctor, doctor_id)

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    statement = (
        select(Appointment, Patient, Doctor)
        .join(Patient, Appointment.patient_id == Patient.id)
        .join(Doctor, Appointment.doctor_id == Doctor.id)
        .where(Appointment.doctor_id == doctor_id)
        .order_by(
            Appointment.appointment_date,
            Appointment.appointment_time
        )
    )

    results = session.exec(statement).all()

    response = []

    for appointment, patient, doctor in results:
        response.append({
            "id": appointment.id,
            "patient_id": appointment.patient_id,
            "patient_name": patient.name,
            "doctor_id": appointment.doctor_id,
            "doctor_name": doctor.name,
            "appointment_date": appointment.appointment_date,
            "appointment_time": appointment.appointment_time
        })

    return response

@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    session: Session = Depends(get_session)
):
    statement = (
        select(Appointment, Patient, Doctor)
        .join(Patient, Appointment.patient_id == Patient.id)
        .join(Doctor, Appointment.doctor_id == Doctor.id)
        .where(Appointment.id == appointment_id)
    )

    result = session.exec(statement).first()

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    appointment, patient, doctor = result

    return {
        "id": appointment.id,
        "patient_id": appointment.patient_id,
        "patient_name": patient.name,
        "doctor_id": appointment.doctor_id,
        "doctor_name": doctor.name,
        "appointment_date": appointment.appointment_date,
        "appointment_time": appointment.appointment_time
    }


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
    existing_appointment = session.exec(
    select(Appointment).where(
        Appointment.doctor_id == updated_appointment.doctor_id,
        Appointment.appointment_date == updated_appointment.appointment_date.isoformat(),
        Appointment.appointment_time == updated_appointment.appointment_time.strftime("%H:%M"),
        Appointment.id != appointment_id
        )
    ).first()

    if existing_appointment:
        raise HTTPException(
            status_code=400,
            detail="Doctor already has another appointment at this date and time"
        )

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