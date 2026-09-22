from fastapi import HTTPException
from sqlmodel import Session, select
from datetime import date, datetime, timedelta

from app.models.appointment import Appointment
from app.models.patient import Patient
from app.models.doctor import Doctor

from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse
)
def generate_time_slots():
    slots = []

    current_time = datetime.strptime(
        "10:00",
        "%H:%M"
    )

    end_time = datetime.strptime(
        "20:00",
        "%H:%M"
    )

    while current_time < end_time:

        slots.append(
            current_time.strftime("%H:%M")
        )

        current_time += timedelta(minutes=30)

    return slots
def get_available_slots(
    doctor_id: int,
    appointment_date: date,
    session: Session
):
    doctor = session.get(Doctor, doctor_id)

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    all_slots = generate_time_slots()

    existing_appointments = session.exec(
        select(Appointment).where(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == appointment_date.isoformat()
        )
    ).all()

    booked_slots = {
        appointment.appointment_time
        for appointment in existing_appointments
    }
    current_time = datetime.now().strftime("%H:%M")
    today = date.today().isoformat()

    slots = []

    for slot in all_slots:

        is_booked = slot in booked_slots

        is_past = (
            appointment_date.isoformat() == today
            and slot <= current_time
        )

        slots.append({
            "time": slot,
            "available": not is_booked and not is_past
        })

    return slots

def create_appointment(
    appointment: AppointmentCreate,
    user_id: int,
    session: Session
):
    patient = session.exec(
        select(Patient).where(
            Patient.user_id == user_id
        )
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient profile not found"
        )

    doctor = session.get(Doctor, appointment.doctor_id)

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    if appointment.appointment_date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Appointment date cannot be in the past"
        )

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

    new_appointment = Appointment(
        patient_id=patient.id,
        doctor_id=appointment.doctor_id,
        appointment_date=appointment.appointment_date.isoformat(),
        appointment_time=appointment.appointment_time.strftime("%H:%M")
    )

    session.add(new_appointment)
    session.commit()
    session.refresh(new_appointment)

    return new_appointment


def update_appointment(
    appointment_id: int,
    updated_appointment: AppointmentUpdate,
    session: Session
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

    if updated_appointment.appointment_date < date.today():
        raise HTTPException(
            status_code=400,
            detail="Appointment date cannot be in the past"
        )

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

    appointment.patient_id = updated_appointment.patient_id
    appointment.doctor_id = updated_appointment.doctor_id
    appointment.appointment_date = updated_appointment.appointment_date.isoformat()
    appointment.appointment_time = updated_appointment.appointment_time.strftime("%H:%M")

    session.add(appointment)
    session.commit()
    session.refresh(appointment)

    return appointment


def delete_appointment(
    appointment_id: int,
    session: Session
):
    appointment = session.get(Appointment, appointment_id)

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    session.delete(appointment)
    session.commit()

    return {
        "message": "Appointment deleted successfully"
    }


def get_appointment(
    appointment_id: int,
    session: Session
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


def get_appointments(
    session: Session
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


def get_patient_appointments(
    patient_id: int,
    session: Session
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


def get_doctor_appointments(
    doctor_id: int,
    session: Session
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
            "doctor_id": doctor.id,
            "doctor_name": doctor.name,
            "appointment_date": appointment.appointment_date,
            "appointment_time": appointment.appointment_time
        })

    return response

def get_my_patient_appointments(
    user_id: int,
    session: Session
):
    patient = session.exec(
        select(Patient).where(
            Patient.user_id == user_id
        )
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient profile not found"
        )

    return get_patient_appointments(
        patient.id,
        session
    )
def get_my_doctor_appointments(
    user_id: int,
    session: Session
):
    doctor = session.exec(
        select(Doctor).where(
            Doctor.user_id == user_id
        )
    ).first()

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor profile not found"
        )

    return get_doctor_appointments(
        doctor.id,
        session
    )
