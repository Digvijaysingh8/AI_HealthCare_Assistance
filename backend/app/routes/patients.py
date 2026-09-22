from fastapi import APIRouter, Depends , HTTPException
from sqlmodel import Session , select
from app.services import patient_service
from app.models.patient import Patient
from app.database.session import get_session
from app.schemas.patient import PatientCreate , PatientUpdate
from app.auth.dependencies import require_role
from app.models.user import User

router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)


@router.post("/")
def create_patient(
    patient: PatientCreate,
    session: Session = Depends(get_session)
):
    return patient_service.create_patient(
        patient,
        session
    )


@router.get("/")
def get_patients(
    session: Session = Depends(get_session)
):
    return patient_service.get_patients(
        session
    )

@router.get("/{patient_id}")
def get_patient(
    patient_id: int,
    session: Session = Depends(get_session)
):
    return patient_service.get_patient(
        patient_id,
        session
    )

@router.delete("/{patient_id}")
def delete_patient(
    patient_id: int,
    current_user: User = Depends(
        require_role(["admin"])
    ),
    session: Session = Depends(get_session)
):
    return patient_service.delete_patient(
        patient_id,
        session
    )

@router.put("/{patient_id}")
def update_patient(
    patient_id: int,
    updated_patient: PatientUpdate,
    current_user: User = Depends(
        require_role(["admin"])
    ),
    session: Session = Depends(get_session)
):
    return patient_service.update_patient(
        patient_id,
        updated_patient,
        session
    )