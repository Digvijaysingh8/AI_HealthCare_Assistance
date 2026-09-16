from fastapi import APIRouter, Depends , HTTPException
from sqlmodel import Session, select

from app.models.doctor import Doctor
from app.database.session import get_session
from app.schemas.doctor import DoctorCreate , DoctorUpdate


router = APIRouter(
    prefix="/doctors",
    tags=["Doctors"]
)


@router.post("/")
def create_doctor(
    doctor: DoctorCreate,
    session: Session = Depends(get_session)
):
    new_doctor=Doctor(
        name=doctor.name,
        specialization = doctor.specialization
    )
    session.add(new_doctor)
    session.commit()
    session.refresh(new_doctor)

    return new_doctor


@router.get("/")
def get_doctors(
    session: Session = Depends(get_session)
):
    doctors = session.exec(
        select(Doctor)
    ).all()

    return doctors


@router.get("/{doctor_id}")
def get_doctor(
    doctor_id: int,
    session: Session = Depends(get_session)
):
    doctor = session.get(Doctor, doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    return doctor


@router.put("/{doctor_id}")
def update_doctor(
    doctor_id: int,
    updated_doctor: DoctorUpdate,
    session: Session = Depends(get_session)
):
    doctor = session.get(Doctor, doctor_id)

    if not doctor:
        return {"message": "Doctor not found"}

    doctor.name = updated_doctor.name
    doctor.specialization = updated_doctor.specialization

    session.add(doctor)
    session.commit()
    session.refresh(doctor)

    return doctor


@router.delete("/{doctor_id}")
def delete_doctor(
    doctor_id: int,
    session: Session = Depends(get_session)
):
    doctor = session.get(Doctor, doctor_id)

    if not doctor:
        return {"message": "Doctor not found"}

    session.delete(doctor)
    session.commit()

    return {"message": "Doctor deleted successfully"}