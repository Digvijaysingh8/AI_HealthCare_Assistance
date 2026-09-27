
import pytest
from fastapi import HTTPException
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorUpdate
from app.services.doctor_service import (
    create_doctor,
    get_doctors,
    get_doctor,
    update_doctor,
    delete_doctor,
)


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create only the Doctor table in an isolated database.
    Doctor.__table__.create(engine)

    with Session(engine) as db:
        yield db

    engine.dispose()


def test_get_doctors_empty(session):
    assert get_doctors(session) == []


def test_get_doctors_returns_all(session):
    session.add_all([
        Doctor(name="Dr. Sharma", specialization="Cardiology"),
        Doctor(name="Dr. Patel", specialization="Neurology"),
    ])
    session.commit()

    doctors = get_doctors(session)

    assert len(doctors) == 2
    assert {d.name for d in doctors} == {
        "Dr. Sharma",
        "Dr. Patel",
    }


def test_get_doctor_success(session):
    doctor = Doctor(
        name="Dr. Sharma",
        specialization="Cardiology",
    )
    session.add(doctor)
    session.commit()
    session.refresh(doctor)

    result = get_doctor(doctor.id, session)

    assert result.id == doctor.id
    assert result.name == "Dr. Sharma"


def test_get_doctor_not_found(session):
    with pytest.raises(HTTPException) as exc:
        get_doctor(999, session)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Doctor not found"


def test_create_doctor(session):
    doctor_data = DoctorCreate(
        name="Dr. Mehta",
        specialization="Dermatology",
    )

    result = create_doctor(doctor_data, session)

    assert result.id is not None
    assert result.name == "Dr. Mehta"
    assert result.specialization == "Dermatology"


def test_update_doctor(session):
    doctor = Doctor(
        name="Dr. Sharma",
        specialization="Cardiology",
    )
    session.add(doctor)
    session.commit()
    session.refresh(doctor)

    updated_data = DoctorUpdate(
        name="Dr. Sharma Updated",
        specialization="Neurology",
    )

    result = update_doctor(doctor.id, updated_data, session)

    assert result.name == "Dr. Sharma Updated"
    assert result.specialization == "Neurology"


def test_update_doctor_not_found(session):
    updated_data = DoctorUpdate(
        name="Dr. New",
        specialization="Cardiology",
    )

    with pytest.raises(HTTPException) as exc:
        update_doctor(999, updated_data, session)

    assert exc.value.status_code == 404


def test_delete_doctor(session):
    doctor = Doctor(
        name="Dr. Sharma",
        specialization="Cardiology",
    )
    session.add(doctor)
    session.commit()
    session.refresh(doctor)

    result = delete_doctor(doctor.id, session)

    assert result == {"message": "Doctor deleted successfully"}
    assert session.get(Doctor, doctor.id) is None


def test_delete_doctor_not_found(session):
    with pytest.raises(HTTPException) as exc:
        delete_doctor(999, session)

    assert exc.value.status_code == 404