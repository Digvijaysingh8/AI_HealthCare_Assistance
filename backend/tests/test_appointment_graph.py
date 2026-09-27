
import uuid
from datetime import date, timedelta

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select
from langgraph.types import Command

import app.agent.appointment_flow as appointment_flow
from app.agent.appointment_flow import (
    appointment_graph,
    book_appointment_node,
)
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment


@pytest.fixture
def booking_env(monkeypatch):
    # Use a separate in-memory database for every test.
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    for model in (User, Patient, Doctor, Appointment):
        model.__table__.create(test_engine)

    # Ensure the graph uses the test database, not the real one.
    monkeypatch.setattr(
        appointment_flow,
        "engine",
        test_engine,
    )

    with Session(test_engine) as session:
        user = User(
            email="testpatient@example.com",
            password_hash="test-hash",
            role="patient",
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        patient = Patient(
            user_id=user.id,
            name="Test Patient",
            age=30,
            gender="Male",
        )
        doctor = Doctor(
            name="Dr. Sharma",
            specialization="Cardiology",
        )

        session.add_all([patient, doctor])
        session.commit()
        session.refresh(patient)
        session.refresh(doctor)

        env = {
            "engine": test_engine,
            "user_id": user.id,
            "patient_id": patient.id,
            "doctor_id": doctor.id,
        }

    yield env
    test_engine.dispose()


def make_state(env, **overrides):
    state = {
        "user_id": env["user_id"],
        "doctor_name": "Dr. Sharma",
        "doctor_id": None,
        "appointment_date": (
            date.today() + timedelta(days=7)
        ).isoformat(),
        "appointment_time": "11:30",
        "confirmed": False,
        "pending_booking": None,
        "response": None,
        "status": None,
    }
    state.update(overrides)
    return state


def make_config():
    return {
        "configurable": {
            "thread_id": str(uuid.uuid4())
        }
    }


def count_appointments(engine):
    with Session(engine) as session:
        return len(
            session.exec(select(Appointment)).all()
        )


@pytest.mark.asyncio
async def test_appointment_waits_for_confirmation(booking_env):
    state = make_state(booking_env)
    config = make_config()

    result = await appointment_graph.ainvoke(
        state,
        config=config,
    )

    assert result.get("__interrupt__")
    assert result["status"] == "ready_for_confirmation"
    assert result["pending_booking"]["doctor_id"] == (
        booking_env["doctor_id"]
    )
    assert count_appointments(booking_env["engine"]) == 0


@pytest.mark.asyncio
async def test_confirmed_appointment_is_booked(booking_env):
    state = make_state(booking_env)
    config = make_config()

    # The graph should pause before booking.
    first_result = await appointment_graph.ainvoke(
        state,
        config=config,
    )

    assert first_result.get("__interrupt__")
    assert count_appointments(booking_env["engine"]) == 0

    # Resume with explicit approval.
    result = await appointment_graph.ainvoke(
        Command(resume=True),
        config=config,
    )

    assert result["status"] == "booked"
    assert result["confirmed"] is True
    assert result["appointment_id"] is not None
    assert "Appointment booked successfully" in result["response"]

    with Session(booking_env["engine"]) as session:
        appointments = session.exec(
            select(Appointment)
        ).all()

        assert len(appointments) == 1
        assert appointments[0].patient_id == (
            booking_env["patient_id"]
        )
        assert appointments[0].doctor_id == (
            booking_env["doctor_id"]
        )
        assert appointments[0].appointment_time == "11:30"


@pytest.mark.asyncio
async def test_cancelled_appointment_is_not_booked(booking_env):
    state = make_state(booking_env)
    config = make_config()

    first_result = await appointment_graph.ainvoke(
        state,
        config=config,
    )

    assert first_result.get("__interrupt__")

    result = await appointment_graph.ainvoke(
        Command(resume=False),
        config=config,
    )

    assert result["status"] == "cancelled"
    assert result["confirmed"] is False
    assert count_appointments(booking_env["engine"]) == 0


@pytest.mark.asyncio
async def test_already_booked_slot_is_rejected(booking_env):
    with Session(booking_env["engine"]) as session:
        session.add(
            Appointment(
                patient_id=booking_env["patient_id"],
                doctor_id=booking_env["doctor_id"],
                appointment_date=(
                    date.today() + timedelta(days=7)
                ).isoformat(),
                appointment_time="11:30",
            )
        )
        session.commit()

    result = await appointment_graph.ainvoke(
        make_state(booking_env),
        config=make_config(),
    )

    assert result["status"] == "unavailable"
    assert "__interrupt__" not in result
    assert count_appointments(booking_env["engine"]) == 1


@pytest.mark.asyncio
async def test_invalid_time_is_rejected(booking_env):
    result = await appointment_graph.ainvoke(
        make_state(
            booking_env,
            appointment_time="invalid-time",
        ),
        config=make_config(),
    )

    assert result["status"] == "error"
    assert "Invalid date or time" in result["response"]
    assert count_appointments(booking_env["engine"]) == 0


@pytest.mark.asyncio
async def test_past_appointment_date_is_rejected(booking_env):
    yesterday = date.today() - timedelta(days=1)

    result = await appointment_graph.ainvoke(
        make_state(
            booking_env,
            appointment_date=yesterday.isoformat(),
        ),
        config=make_config(),
    )

    assert result["status"] == "unavailable"
    assert "past" in result["response"].lower()
    assert count_appointments(booking_env["engine"]) == 0


@pytest.mark.asyncio
async def test_unknown_doctor_is_rejected(booking_env):
    result = await appointment_graph.ainvoke(
        make_state(
            booking_env,
            doctor_name="Unknown Doctor",
        ),
        config=make_config(),
    )

    assert result["status"] == "error"
    assert result["response"] == "Doctor not found."
    assert count_appointments(booking_env["engine"]) == 0


def test_unconfirmed_booking_is_rejected(booking_env):
    state = make_state(
        booking_env,
        confirmed=False,
        pending_booking={
            "patient_id": booking_env["patient_id"],
            "doctor_id": booking_env["doctor_id"],
            "appointment_date": (
                date.today() + timedelta(days=7)
            ).isoformat(),
            "appointment_time": "11:30",
            "doctor_name": "Dr. Sharma",
        },
    )

    result = book_appointment_node(state)

    assert result["status"] == "error"
    assert "confirmation is required" in result["response"]
    assert count_appointments(booking_env["engine"]) == 0


@pytest.mark.asyncio
async def test_doctor_role_cannot_book(booking_env):
    with Session(booking_env["engine"]) as session:
        doctor_user = User(
            email="doctor@example.com",
            password_hash="test-hash",
            role="doctor",
        )
        session.add(doctor_user)
        session.commit()
        session.refresh(doctor_user)
        doctor_user_id = doctor_user.id

    result = await appointment_graph.ainvoke(
        make_state(
            booking_env,
            user_id=doctor_user_id,
        ),
        config=make_config(),
    )

    assert result["status"] == "error"
    assert "Only authenticated patients" in result["response"]
    assert count_appointments(booking_env["engine"]) == 0