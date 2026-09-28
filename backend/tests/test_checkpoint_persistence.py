
from datetime import date, timedelta

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine, select
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.types import Command

import app.agent.appointment_flow as appointment_flow
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment


@pytest.mark.asyncio
async def test_checkpoint_survives_reopening(tmp_path, monkeypatch):
    # Separate application database for this test.
    app_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    SQLModel.metadata.create_all(app_engine)
    monkeypatch.setattr(
        appointment_flow, "engine", app_engine
    )

    with Session(app_engine) as session:
        user = User(
            email="checkpoint-test@example.com",
            password_hash="test-hash",
            role="patient",
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        patient = Patient(
            user_id=user.id,
            name="Checkpoint Patient",
            age=30,
            gender="Male",
        )
        doctor = Doctor(
            name="Dr. Checkpoint",
            specialization="Cardiology",
        )
        session.add_all([patient, doctor])
        session.commit()
        session.refresh(doctor)

        user_id = user.id

    # Use a temporary, file-based checkpoint database.
    checkpoint_path = str(tmp_path / "checkpoints.sqlite")
    config = {
        "configurable": {
            "thread_id": "persistence-test-001"
        }
    }

    state = {
        "user_id": user_id,
        "doctor_name": "Dr. Checkpoint",
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

    # First connection: pause before confirmation.
    async with AsyncSqliteSaver.from_conn_string(
        checkpoint_path
    ) as saver:
        await saver.setup()
        appointment_flow.set_appointment_checkpointer(saver)

        result = await appointment_flow.appointment_graph.ainvoke(
            state,
            config=config,
        )

        assert result.get("__interrupt__")
        assert result["status"] == "ready_for_confirmation"

    # The first saver is now closed, simulating a restart.

    # Second connection: reopen the same checkpoint database.
    async with AsyncSqliteSaver.from_conn_string(
        checkpoint_path
    ) as saver:
        await saver.setup()
        appointment_flow.set_appointment_checkpointer(saver)

        snapshot = await appointment_flow.appointment_graph.aget_state(
            config
        )

        # The pending appointment should still be available.
        assert snapshot.values["user_id"] == user_id
        assert snapshot.values["status"] == "ready_for_confirmation"
        assert snapshot.values["pending_booking"]["doctor_name"] == (
            "Dr. Checkpoint"
        )

        # Cancel rather than book, keeping the test harmless.
        result = await appointment_flow.appointment_graph.ainvoke(
            Command(resume=False),
            config=config,
        )

        assert result["status"] == "cancelled"

    with Session(app_engine) as session:
        appointments = session.exec(
            select(Appointment)
        ).all()
        assert len(appointments) == 0

    app_engine.dispose()