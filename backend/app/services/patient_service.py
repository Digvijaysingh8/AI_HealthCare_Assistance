from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate


def create_patient(
    patient: PatientCreate,
    session: Session
):
    new_patient = Patient(
        name=patient.name,
        age=patient.age,
        gender=patient.gender
    )

    session.add(new_patient)
    session.commit()
    session.refresh(new_patient)

    return new_patient

def update_patient(
    patient_id: int,
    updated_patient: PatientUpdate,
    session: Session
):
    patient = session.get(Patient, patient_id)

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    patient.name = updated_patient.name
    patient.age = updated_patient.age
    patient.gender = updated_patient.gender

    session.add(patient)
    session.commit()
    session.refresh(patient)

    return patient

def get_patients(
    session: Session
):
    patients = session.exec(
        select(Patient)
    ).all()

    return patients

def get_patient(
    patient_id: int,
    session: Session
):
    patient = session.get(Patient, patient_id)

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient

def delete_patient(
    patient_id: int,
    session: Session
):
    patient = session.get(Patient, patient_id)

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    session.delete(patient)
    session.commit()

    return {
        "message": "Patient deleted successfully"
    }