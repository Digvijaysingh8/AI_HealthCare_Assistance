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
    current_user: User = Depends(
        require_role(["admin", "patient"])
    ),
    session: Session = Depends(get_session)
):
    user_id = (
        current_user.id
        if current_user.role == "patient"
        else None
    )

    return patient_service.create_patient(
        patient,
        session,
        user_id=user_id
    )


@router.get("/")
def get_patients(
    current_user: User = Depends(
        require_role(["admin"])
    ),
    session: Session = Depends(get_session)
):
    return patient_service.get_patients(session)
@router.get("/me")
def get_my_patient(
    current_user: User = Depends(require_role(["patient"])),
    session: Session = Depends(get_session)
):
    patient = session.exec(
        select(Patient).where(Patient.user_id == current_user.id)
    ).first()

    if not patient:
        raise HTTPException(
            status_code=404,
            detail="Patient profile not found"
        )

    return patient


@router.get("/{patient_id}")
def get_patient(
    patient_id: int,
    current_user: User = Depends(
        require_role(["admin", "patient"])
    ),
    session: Session = Depends(get_session)
):
    patient = patient_service.get_patient(
        patient_id,
        session
    )

    if (
        current_user.role == "patient"
        and patient.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this resource"
        )

    return patient

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