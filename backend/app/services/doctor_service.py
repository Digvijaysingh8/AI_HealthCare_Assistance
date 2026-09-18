from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate


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