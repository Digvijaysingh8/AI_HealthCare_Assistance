from fastapi import APIRouter, Depends , HTTPException
from sqlmodel import Session, select
from app.services import doctor_service
from app.models.doctor import Doctor
from app.database.session import get_session
from app.schemas.doctor import DoctorCreate , DoctorUpdate

from app.auth.dependencies import require_role
from app.models.user import User
router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)


@router.post("/")
def create_doctor(
    doctor: DoctorCreate,
    current_user: User = Depends(
        require_role(["admin"])
    ),
    session: Session = Depends(get_session)
):
    return doctor_service.create_doctor(
        doctor,
        session
    )


@router.get("/")
def get_doctors(
    session: Session = Depends(get_session)
):
    return doctor_service.get_doctors(
        session
    )
@router.get("/my-patients")
def get_my_patients(
    current_user: User = Depends(
        require_role(["doctor"])
    ),
    session: Session = Depends(get_session)
):
    return doctor_service.get_my_patients(
        current_user.id,
        session
    )

@router.get("/{doctor_id}")
def get_doctor(
    doctor_id: int,
    session: Session = Depends(get_session)
):
   return doctor_service.get_doctor(
        doctor_id,
        session
    )


@router.put("/{doctor_id}")
def update_doctor(
    doctor_id: int,
    updated_doctor: DoctorUpdate,
    current_user: User = Depends(
        require_role(["admin"])
    ),
    session: Session = Depends(get_session)
):
    return doctor_service.update_doctor(
        doctor_id,
        updated_doctor,
        session
    )

@router.delete("/{doctor_id}")
def delete_doctor(
    doctor_id: int,
    current_user: User = Depends(
        require_role(["admin"])
    ),
    session: Session = Depends(get_session)
):
    return doctor_service.delete_doctor(
        doctor_id,
        session
    )
