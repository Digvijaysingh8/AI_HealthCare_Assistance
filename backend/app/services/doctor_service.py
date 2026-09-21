from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate
from app.models.patient import Patient
from app.models.appointment import Appointment

def create_doctor(
    doctor: DoctorCreate,
    session: Session
):
    new_doctor = Doctor(
        name=doctor.name,
        specialization=doctor.specialization
    )

    session.add(new_doctor)
    session.commit()
    session.refresh(new_doctor)

    return new_doctor


def get_doctors(
    session: Session
):
    doctors = session.exec(
        select(Doctor)
    ).all()

    return doctors


def get_doctor(
    doctor_id: int,
    session: Session
):
    doctor = session.get(Doctor, doctor_id)

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return doctor


def update_doctor(
    doctor_id: int,
    updated_doctor: DoctorUpdate,
    session: Session
):
    doctor = session.get(Doctor, doctor_id)

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    doctor.name = updated_doctor.name
    doctor.specialization = updated_doctor.specialization

    session.add(doctor)
    session.commit()
    session.refresh(doctor)

    return doctor


def delete_doctor(
    doctor_id: int,
    session: Session
):
    doctor = session.get(Doctor, doctor_id)

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    session.delete(doctor)
    session.commit()

    return {
        "message": "Doctor deleted successfully"
    }

def get_my_patients(
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

    statement = (
        select(Patient)
        .join(
            Appointment,
            Appointment.patient_id == Patient.id
        )
        .where(
            Appointment.doctor_id == doctor.id
        )
        .distinct()
    )

    patients = session.exec(statement).all()

    return patients