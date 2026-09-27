
import pytest
from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.main import app
from app.database.session import get_session
from app.auth.jwt import create_access_token
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment


@pytest.fixture
def test_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def client(test_engine, monkeypatch):
    def override_get_session():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    # Prevent test startup from touching the real database.
    monkeypatch.setattr(
        "app.main.create_db_and_tables",
        lambda: None,
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.pop(get_session, None)


def create_identity(engine, role, email=None):
    email = email or f"{role}@example.com"

    with Session(engine) as session:
        user = User(
            email=email,
            password_hash="test-hash",
            role=role,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id

    token = create_access_token({
        "sub": str(user_id),
        "role": role,
    })

    return {
        "id": user_id,
        "email": email,
        "headers": {
            "Authorization": f"Bearer {token}"
        },
    }


def create_patient_identity(engine, email):
    identity = create_identity(
        engine,
        "patient",
        email,
    )

    with Session(engine) as session:
        patient = Patient(
            user_id=identity["id"],
            name="Test Patient",
            age=30,
            gender="Male",
        )
        session.add(patient)
        session.commit()
        session.refresh(patient)
        patient_id = patient.id

    identity["patient_id"] = patient_id
    return identity


def create_doctor(engine):
    with Session(engine) as session:
        doctor = Doctor(
            name="Dr. Sharma",
            specialization="Cardiology",
        )
        session.add(doctor)
        session.commit()
        session.refresh(doctor)
        return doctor.id


def register_payload(email, role="patient"):
    return {
        "name": "Test User",
        "email": email,
        "password": "TestPassword123",
        "age": 30,
        "gender": "Male",
        "role": role,
    }


def future_date():
    return (date.today() + timedelta(days=7)).isoformat()


# ---------------- HOME ----------------

def test_home_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == (
        "AI Healthcare Assistant API is running"
    )


# ---------------- AUTHENTICATION ----------------

def test_register_patient(client, test_engine):
    response = client.post(
        "/auth/register",
        json=register_payload("newpatient@example.com"),
    )

    assert response.status_code == 200
    assert response.json()["email"] == "newpatient@example.com"
    assert response.json()["role"] == "patient"

    with Session(test_engine) as session:
        user = session.get(User, response.json()["id"])
        patient = session.exec(
            SQLModel.select(Patient).where(
                Patient.user_id == user.id
            )
        ).first() if False else session.query(Patient).filter_by(
            user_id=user.id
        ).first()

        assert user is not None
        assert patient is not None


def test_register_duplicate_email(client):
    payload = register_payload("duplicate@example.com")

    first = client.post("/auth/register", json=payload)
    second = client.post("/auth/register", json=payload)

    assert first.status_code == 200
    assert second.status_code == 400


def test_register_invalid_role(client):
    response = client.post(
        "/auth/register",
        json=register_payload(
            "invalidrole@example.com",
            role="superuser",
        ),
    )

    assert response.status_code == 400


def test_register_rejects_public_admin(client):
    response = client.post(
        "/auth/register",
        json=register_payload(
            "newadmin@example.com",
            role="admin",
        ),
    )

    # Expected security behavior.
    # Currently this is likely to fail because public
    # registration accepts the admin role.
    assert response.status_code == 400


def test_login_success(client):
    client.post(
        "/auth/register",
        json=register_payload("login@example.com"),
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["email"] == "login@example.com"


def test_login_invalid_password(client):
    client.post(
        "/auth/register",
        json=register_payload("wrongpass@example.com"),
    )

    response = client.post(
        "/auth/login",
        json={
            "email": "wrongpass@example.com",
            "password": "WrongPassword",
        },
    )

    assert response.status_code == 401


def test_me_requires_authentication(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_returns_authenticated_user(client, test_engine):
    identity = create_identity(
        test_engine,
        "patient",
        "me@example.com",
    )

    response = client.get(
        "/auth/me",
        headers=identity["headers"],
    )

    assert response.status_code == 200
    assert response.json()["id"] == identity["id"]
    assert response.json()["email"] == identity["email"]


def test_me_rejects_invalid_token(client):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


def test_role_based_access(client, test_engine):
    patient = create_identity(
        test_engine, "patient", "rolepatient@example.com"
    )
    doctor = create_identity(
        test_engine, "doctor", "roledoctor@example.com"
    )

    assert client.get(
        "/auth/patient-only",
        headers=patient["headers"],
    ).status_code == 200

    assert client.get(
        "/auth/doctor-only",
        headers=doctor["headers"],
    ).status_code == 200

    assert client.get(
        "/auth/patient-only",
        headers=doctor["headers"],
    ).status_code == 403

    assert client.get(
        "/auth/doctor-only",
        headers=patient["headers"],
    ).status_code == 403


# ---------------- DOCTOR API ----------------

def test_get_doctors_public(client, test_engine):
    doctor_id = create_doctor(test_engine)

    response = client.get("/doctors/")

    assert response.status_code == 200
    assert any(
        doctor["id"] == doctor_id
        for doctor in response.json()
    )


def test_create_doctor_as_admin(client, test_engine):
    admin = create_identity(test_engine, "admin")

    response = client.post(
        "/doctors/",
        headers=admin["headers"],
        json={
            "name": "Dr. Patel",
            "specialization": "Neurology",
        },
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Dr. Patel"


def test_patient_cannot_create_doctor(client, test_engine):
    patient = create_identity(test_engine, "patient")

    response = client.post(
        "/doctors/",
        headers=patient["headers"],
        json={
            "name": "Dr. New",
            "specialization": "Cardiology",
        },
    )

    assert response.status_code == 403


def test_non_admin_cannot_update_or_delete_doctor(
    client, test_engine
):
    doctor_id = create_doctor(test_engine)
    patient = create_identity(test_engine, "patient")

    update_response = client.put(
        f"/doctors/{doctor_id}",
        headers=patient["headers"],
        json={
            "name": "Dr. Changed",
            "specialization": "Neurology",
        },
    )

    delete_response = client.delete(
        f"/doctors/{doctor_id}",
        headers=patient["headers"],
    )

    assert update_response.status_code == 403
    assert delete_response.status_code == 403


# ---------------- APPOINTMENT API ----------------

def test_patient_can_create_appointment(
    client, test_engine
):
    patient = create_patient_identity(
        test_engine,
        "bookingpatient@example.com",
    )
    doctor_id = create_doctor(test_engine)

    response = client.post(
        "/appointments/",
        headers=patient["headers"],
        json={
            # The service should use the authenticated
            # patient's profile, not this supplied ID.
            "patient_id": 9999,
            "doctor_id": doctor_id,
            "appointment_date": future_date(),
            "appointment_time": "11:30:00",
        },
    )

    assert response.status_code == 200
    assert response.json()["patient_id"] == patient["patient_id"]
    assert response.json()["doctor_id"] == doctor_id


def test_non_patient_cannot_create_appointment(
    client, test_engine
):
    doctor = create_identity(test_engine, "doctor")

    response = client.post(
        "/appointments/",
        headers=doctor["headers"],
        json={
            "patient_id": 1,
            "doctor_id": 1,
            "appointment_date": future_date(),
            "appointment_time": "11:30:00",
        },
    )

    assert response.status_code == 403


def test_duplicate_appointment_rejected(
    client, test_engine
):
    patient = create_patient_identity(
        test_engine,
        "duplicatebooking@example.com",
    )
    doctor_id = create_doctor(test_engine)

    payload = {
        "patient_id": patient["patient_id"],
        "doctor_id": doctor_id,
        "appointment_date": future_date(),
        "appointment_time": "11:30:00",
    }

    first = client.post(
        "/appointments/",
        headers=patient["headers"],
        json=payload,
    )
    second = client.post(
        "/appointments/",
        headers=patient["headers"],
        json=payload,
    )

    assert first.status_code == 200
    assert second.status_code == 400


def test_my_appointments_returns_patient_bookings(
    client, test_engine
):
    patient = create_patient_identity(
        test_engine,
        "mybookings@example.com",
    )
    doctor_id = create_doctor(test_engine)

    booking = client.post(
        "/appointments/",
        headers=patient["headers"],
        json={
            "patient_id": patient["patient_id"],
            "doctor_id": doctor_id,
            "appointment_date": future_date(),
            "appointment_time": "12:00:00",
        },
    )
    assert booking.status_code == 200

    response = client.get(
        "/appointments/my",
        headers=patient["headers"],
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["doctor_id"] == doctor_id


def test_my_appointments_rejects_doctor(
    client, test_engine
):
    doctor = create_identity(test_engine, "doctor")

    response = client.get(
        "/appointments/my",
        headers=doctor["headers"],
    )

    assert response.status_code == 403


def test_available_slots_unknown_doctor(client):
    response = client.get(
        "/appointments/available-slots/999",
        params={"appointment_date": future_date()},
    )

    assert response.status_code == 404


def test_patient_cannot_read_all_appointments(
    client, test_engine
):
    patient = create_identity(
        test_engine,
        "patient",
        "listpatient@example.com",
    )

    response = client.get(
        "/appointments/",
        headers=patient["headers"],
    )

    # Expected privacy behavior: general users should not
    # be allowed to retrieve every patient's appointments.
    # The current route only checks authentication.
    assert response.status_code == 403


def test_patient_cannot_read_another_patient_appointments(
    client, test_engine
):
    viewer = create_patient_identity(
        test_engine,
        "viewer@example.com",
    )
    other = create_patient_identity(
        test_engine,
        "other@example.com",
    )
    doctor_id = create_doctor(test_engine)

    with Session(test_engine) as session:
        session.add(
            Appointment(
                patient_id=other["patient_id"],
                doctor_id=doctor_id,
                appointment_date=future_date(),
                appointment_time="13:00",
            )
        )
        session.commit()

    response = client.get(
        f"/appointments/patient/{other['patient_id']}",
        headers=viewer["headers"],
    )

    # Expected privacy behavior. Current route allows
    # any authenticated user to request any patient ID.
    assert response.status_code == 403


def test_patient_cannot_read_another_appointment(
    client, test_engine
):
    viewer = create_patient_identity(
        test_engine,
        "appointmentviewer@example.com",
    )
    other = create_patient_identity(
        test_engine,
        "appointmentowner@example.com",
    )
    doctor_id = create_doctor(test_engine)

    with Session(test_engine) as session:
        appointment = Appointment(
            patient_id=other["patient_id"],
            doctor_id=doctor_id,
            appointment_date=future_date(),
            appointment_time="13:30",
        )
        session.add(appointment)
        session.commit()
        session.refresh(appointment)
        appointment_id = appointment.id

    response = client.get(
        f"/appointments/{appointment_id}",
        headers=viewer["headers"],
    )

    # Expected privacy behavior; the existing route
    # does not check appointment ownership.
    assert response.status_code == 403


# ---------------- AI API ----------------

def test_ai_chat_requires_authentication(client):
    response = client.post(
        "/ai/chat",
        json={"question": "What are diabetes symptoms?"},
    )

    assert response.status_code == 401


def test_ai_chat_returns_mocked_response(
    client, test_engine, monkeypatch
):
    patient = create_identity(
        test_engine,
        "patient",
        "aiuser@example.com",
    )

    async def fake_ask_healthcare_assistant(
        question,
        user_id,
        thread_id=None,
        confirmed=False,
    ):
        return {
            "answer": "Mock AI response",
            "thread_id": "test-thread",
            "requires_confirmation": True,
            "pending_booking": {"doctor_id": 1},
        }

    monkeypatch.setattr(
        "app.routes.ai.ask_healthcare_assistant",
        fake_ask_healthcare_assistant,
    )

    response = client.post(
        "/ai/chat",
        headers=patient["headers"],
        json={"question": "Book an appointment"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Mock AI response"
    assert data["thread_id"] == "test-thread"
    assert data["requires_confirmation"] is True
    assert data["pending_booking"]["doctor_id"] == 1