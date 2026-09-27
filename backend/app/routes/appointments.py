
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from datetime import date

from app.database.session import get_session
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse
)
from app.auth.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.services import appointment_service


router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


def check_patient_access(
    patient_id: int,
    current_user: User,
    session: Session
):
    # Admin can access any patient's appointments.
    if current_user.role == "admin":
        return

    # Patients can access only their own records.
    if current_user.role == "patient":
        patient = session.exec(
            select(Patient).where(
                Patient.user_id == current_user.id
            )
        ).first()

        if patient and patient.id == patient_id:
            return

    # Doctors can access patients with appointments
    # assigned to their own doctor profile.
    if current_user.role == "doctor":
        doctor = session.exec(
            select(Doctor).where(
                Doctor.user_id == current_user.id
            )
        ).first()

        if doctor:
            appointment = session.exec(
                select(Appointment).where(
                    Appointment.patient_id == patient_id,
                    Appointment.doctor_id == doctor.id
                )
            ).first()

            if appointment:
                return

    raise HTTPException(
        status_code=403,
        detail="You do not have permission to access this patient's appointments"
    )


@router.post("/")
def create_appointment(
    appointment: AppointmentCreate,
    current_user: User = Depends(
        require_role(["patient"])
    ),
    session: Session = Depends(get_session)
):
    return appointment_service.create_appointment(
        appointment,
        current_user.id,
        session
    )


@router.get("/", response_model=list[AppointmentResponse])
def get_appointments(
    current_user: User = Depends(
        require_role(["admin"])
    ),
    session: Session = Depends(get_session)
):
    return appointment_service.get_appointments(session)


@router.get(
    "/patient/{patient_id}",
    response_model=list[AppointmentResponse]
)
def get_patient_appointments(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    check_patient_access(
        patient_id,
        current_user,
        session
    )

    return appointment_service.get_patient_appointments(
        patient_id,
        session
    )


@router.get(
    "/doctor/{doctor_id}",
    response_model=list[AppointmentResponse]
)
def get_doctor_appointments(
    doctor_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    if current_user.role == "admin":
        pass
    elif current_user.role == "doctor":
        doctor = session.exec(
            select(Doctor).where(
                Doctor.user_id == current_user.id
            )
        ).first()

        if not doctor or doctor.id != doctor_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access these appointments"
            )
    else:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access these appointments"
        )

    return appointment_service.get_doctor_appointments(
        doctor_id,
        session
    )


@router.get("/available-slots/{doctor_id}")
def get_available_slots(
    doctor_id: int,
    appointment_date: date,
    session: Session = Depends(get_session)
):
    return appointment_service.get_available_slots(
        doctor_id,
        appointment_date,
        session
    )


@router.get(
    "/my",
    response_model=list[AppointmentResponse]
)
def get_my_patient_appointments(
    current_user: User = Depends(
        require_role(["patient"])
    ),
    session: Session = Depends(get_session)
):
    return appointment_service.get_my_patient_appointments(
        current_user.id,
        session
    )


@router.get(
    "/my-doctor",
    response_model=list[AppointmentResponse]
)
def get_my_doctor_appointments(
    current_user: User = Depends(
        require_role(["doctor"])
    ),
    session: Session = Depends(get_session)
):
    return appointment_service.get_my_doctor_appointments(
        current_user.id,
        session
    )


@router.get(
    "/{appointment_id}",
    response_model=AppointmentResponse
)
def get_appointment(
    appointment_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    appointment = session.get(Appointment, appointment_id)

    if not appointment:
        raise HTTPException(
            status_code=404,
            detail="Appointment not found"
        )

    if current_user.role == "admin":
        pass
    elif current_user.role == "patient":
        patient = session.exec(
            select(Patient).where(
                Patient.user_id == current_user.id
            )
        ).first()

        if not patient or patient.id != appointment.patient_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this appointment"
            )
    elif current_user.role == "doctor":
        doctor = session.exec(
            select(Doctor).where(
                Doctor.user_id == current_user.id
            )
        ).first()

        if not doctor or doctor.id != appointment.doctor_id:
            raise HTTPException(
                status_code=403,
                detail="You do not have permission to access this appointment"
            )
    else:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access this appointment"
        )

    return appointment_service.get_appointment(
        appointment_id,
        session
    )


@router.put("/{appointment_id}")
def update_appointment(
    appointment_id: int,
    updated_appointment: AppointmentUpdate,
    current_user: User = Depends(
        require_role(["admin"])
    ),
    session: Session = Depends(get_session)
):
    return appointment_service.update_appointment(
        appointment_id,
        updated_appointment,
        session
    )


@router.delete("/{appointment_id}")
def delete_appointment(
    appointment_id: int,
    current_user: User = Depends(
        require_role(["admin"])
    ),
    session: Session = Depends(get_session)
):
    return appointment_service.delete_appointment(
        appointment_id,
        session
    )