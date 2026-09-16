from fastapi import APIRouter, Depends , HTTPException
from sqlmodel import Session , select

from app.models.patient import Patient
from app.database.session import get_session
from app.schemas.patient import PatientCreate , PatientUpdate


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.post("/")
def create_patient(
    patient: PatientCreate,
    session: Session = Depends(get_session)
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



@router.get("/")
def get_patient(
    patient_id: int,
    session: Session = Depends(get_session)
):
    patients = session.exec(
        select(Patient)
    ).all()

    return patients


@router.get("/{patient_id}")
def get_patient(
    patient_id: int,
    session: Session = Depends(get_session)
):
    patient = session.get(Patient, patient_id)
    
    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    return patient

@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    session: Session = Depends(get_session)
):
    patient = session.get(Patient, patient_id)

    if not patient:
        return {"message": "Patient not found"}

    session.delete(patient)
    session.commit()

    return {"message": "Patient deleted successfully"}

@router.put("/{patient_id}")
def update_patient(
    patient_id: int,
    updated_patient: PatientUpdate,
    session: Session = Depends(get_session)
):
    patient = session.get(Patient, patient_id)

    if not patient:
        return {"message": "Patient not found"}

    patient.name = updated_patient.name
    patient.age = updated_patient.age
    patient.gender = updated_patient.gender

    session.add(patient)
    session.commit()
    session.refresh(patient)

    return patient