
import pytest
from datetime import date, time, timedelta

from fastapi import HTTPException
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.services.appointment_service import (
    generate_time_slots,
    get_available_slots,
    create_appointment,
    update_appointment,
    delete_appointment,
    get_appointment,
)


@pytest.fixture
def session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Doctor.__table__.create(engine)
    Patient.__table__.create(engine)
    Appointment.__table__.create(engine)

    with Session(engine) as db:
        yield db

    engine.dispose()


@pytest.fixture
def doctor(session):
    item = Doctor(
        name="Dr. Sharma",
        specialization="Cardiology",
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@pytest.fixture
def patient(session):
    item = Patient(
        user_id=1001,
        name="Test Patient",
        age=30,
        gender="Male",
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@pytest.fixture
def future_date():
    return date.today() + timedelta(days=7)


def test_generate_time_slots():
    slots = generate_time_slots()

    assert len(slots) == 20
    assert slots[0] == "10:00"
    assert slots[-1] == "19:30"


def test_get_available_slots(session, doctor, future_date):
    slots = get_available_slots(doctor.id, future_date, session)

    assert len(slots) == 20
    assert all(slot["available"] for slot in slots)


def test_get_available_slots_marks_booked_slot(
    session, doctor, patient, future_date
):
    session.add(
        Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            appointment_date=future_date.isoformat(),
            appointment_time="10:00",
        )
    )
    session.commit()

    slots = get_available_slots(doctor.id, future_date, session)

    first_slot = next(s for s in slots if s["time"] == "10:00")
    second_slot = next(s for s in slots if s["time"] == "10:30")

    assert first_slot["available"] is False
    assert second_slot["available"] is True


def test_get_available_slots_invalid_doctor(session, future_date):
    with pytest.raises(HTTPException) as exc:
        get_available_slots(999, future_date, session)

    assert exc.value.status_code == 404


def test_create_appointment(session, doctor, patient, future_date):
    data = AppointmentCreate(
        patient_id=9999,
        doctor_id=doctor.id,
        appointment_date=future_date,
        appointment_time=time(10, 0),
    )

    result = create_appointment(data, 1001, session)

    assert result.id is not None
    assert result.patient_id == patient.id
    assert result.doctor_id == doctor.id
    assert result.appointment_date == future_date.isoformat()
    assert result.appointment_time == "10:00"


def test_create_appointment_missing_patient(
    session, doctor, future_date
):
    data = AppointmentCreate(
        patient_id=1,
        doctor_id=doctor.id,
        appointment_date=future_date,
        appointment_time=time(10, 0),
    )

    with pytest.raises(HTTPException) as exc:
        create_appointment(data, 9999, session)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Patient profile not found"


def test_create_appointment_missing_doctor(
    session, patient, future_date
):
    data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=999,
        appointment_date=future_date,
        appointment_time=time(10, 0),
    )

    with pytest.raises(HTTPException) as exc:
        create_appointment(data, 1001, session)

    assert exc.value.status_code == 404


def test_create_appointment_past_date(session, doctor, patient):
    data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_date=date.today() - timedelta(days=1),
        appointment_time=time(10, 0),
    )

    with pytest.raises(HTTPException) as exc:
        create_appointment(data, 1001, session)

    assert exc.value.status_code == 400


def test_create_duplicate_appointment(
    session, doctor, patient, future_date
):
    data = AppointmentCreate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_date=future_date,
        appointment_time=time(10, 0),
    )

    create_appointment(data, 1001, session)

    with pytest.raises(HTTPException) as exc:
        create_appointment(data, 1001, session)

    assert exc.value.status_code == 400
    assert "already has an appointment" in exc.value.detail


def test_update_appointment(session, doctor, patient, future_date):
    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_date=future_date.isoformat(),
        appointment_time="10:00",
    )
    session.add(appointment)
    session.commit()
    session.refresh(appointment)

    updated = AppointmentUpdate(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_date=future_date,
        appointment_time=time(11, 0),
    )

    result = update_appointment(appointment.id, updated, session)

    assert result.appointment_time == "11:00"


def test_delete_appointment(session, doctor, patient, future_date):
    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_date=future_date.isoformat(),
        appointment_time="10:00",
    )
    session.add(appointment)
    session.commit()
    session.refresh(appointment)

    result = delete_appointment(appointment.id, session)

    assert result == {"message": "Appointment deleted successfully"}
    assert session.get(Appointment, appointment.id) is None


def test_get_appointment(session, doctor, patient, future_date):
    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_date=future_date.isoformat(),
        appointment_time="10:00",
    )
    session.add(appointment)
    session.commit()
    session.refresh(appointment)

    result = get_appointment(appointment.id, session)

    assert result["patient_name"] == patient.name
    assert result["doctor_name"] == doctor.name
    assert result["appointment_time"] == "10:00"


def test_get_appointment_not_found(session):
    with pytest.raises(HTTPException) as exc:
        get_appointment(999, session)

    assert exc.value.status_code == 404