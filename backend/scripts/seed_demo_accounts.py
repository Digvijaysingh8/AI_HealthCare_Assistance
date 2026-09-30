"""Create a fresh set of working login accounts.

The legacy SQLite data contains user rows that were never linked to a
patient/doctor profile, so those accounts can authenticate but then get a
404 from /patients/me. This creates clean, fully-linked accounts without
touching the existing rows.

Run from the ``backend`` directory:

    python scripts/seed_demo_accounts.py

Idempotent: re-running updates the password of the existing demo accounts
instead of failing on the unique email constraint.
"""

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from sqlmodel import Session, select  # noqa: E402

from app.auth.password import hash_password  # noqa: E402
from app.database.database import engine  # noqa: E402
from app.models.user import User  # noqa: E402
from app.models.patient import Patient  # noqa: E402
from app.models.doctor import Doctor  # noqa: E402

# Demo-only credentials. These are intentionally obvious so nobody mistakes
# them for production secrets; change them before any real deployment.
DEMO_PASSWORD = "Demo@12345"

ACCOUNTS = [
    {
        "email": "demo.admin@odasha.test",
        "role": "admin",
        "patient": None,
        "doctor": None,
    },
    {
        "email": "demo.patient@odasha.test",
        "role": "patient",
        "patient": {"name": "Demo Patient", "age": 29, "gender": "Female"},
        "doctor": None,
    },
    {
        "email": "demo.doctor@odasha.test",
        "role": "doctor",
        "patient": None,
        "doctor": {"name": "Demo Doctor", "specialization": "Cardiology"},
    },
]


def upsert_account(session, spec):
    email = spec["email"]

    user = session.exec(select(User).where(User.email == email)).first()

    if user:
        user.password_hash = hash_password(DEMO_PASSWORD)
        user.role = spec["role"]
        created = False
    else:
        user = User(
            email=email,
            password_hash=hash_password(DEMO_PASSWORD),
            role=spec["role"],
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        created = True

    if spec["patient"]:
        profile = session.exec(
            select(Patient).where(Patient.user_id == user.id)
        ).first()
        if profile:
            for key, value in spec["patient"].items():
                setattr(profile, key, value)
        else:
            session.add(Patient(user_id=user.id, **spec["patient"]))

    if spec["doctor"]:
        profile = session.exec(
            select(Doctor).where(Doctor.user_id == user.id)
        ).first()
        if profile:
            for key, value in spec["doctor"].items():
                setattr(profile, key, value)
        else:
            session.add(Doctor(user_id=user.id, **spec["doctor"]))

    session.commit()
    return user.id, created


def main():
    print("Target: %s\n" % engine.url.render_as_string(hide_password=True))

    created_count = 0
    with Session(engine) as session:
        for spec in ACCOUNTS:
            user_id, created = upsert_account(session, spec)
            created_count += 1 if created else 0
            print(
                "  %-28s role=%-8s id=%-4s %s"
                % (
                    spec["email"],
                    spec["role"],
                    user_id,
                    "created" if created else "password reset",
                )
            )

    print("\n%d account(s) created, %d updated."
          % (created_count, len(ACCOUNTS) - created_count))
    print("Password for all of them: %s" % DEMO_PASSWORD)

    # Verify each account can actually reach its profile endpoints, which is
    # what fails for the unlinked legacy accounts.
    print("\nVerifying login + profile access...")
    import httpx  # noqa: E402

    base = "http://127.0.0.1:8000"
    ok = True

    with httpx.Client(timeout=30) as cli:
        for spec in ACCOUNTS:
            email = spec["email"]
            r = cli.post(base + "/auth/login",
                         json={"email": email, "password": DEMO_PASSWORD})
            if r.status_code != 200:
                print("  %-28s login FAILED (%s)" % (email, r.status_code))
                ok = False
                continue

            token = r.json()["access_token"]
            h = {"Authorization": "Bearer " + token}

            if spec["patient"]:
                p = cli.get(base + "/patients/me", headers=h)
                a = cli.get(base + "/appointments/my", headers=h)
                good = p.status_code == 200 and a.status_code == 200
                print("  %-28s /patients/me=%s /appointments/my=%s"
                      % (email, p.status_code, a.status_code))
            elif spec["doctor"]:
                d = cli.get(base + "/doctors/my-patients", headers=h)
                good = d.status_code == 200
                print("  %-28s /doctors/my-patients=%s" % (email, d.status_code))
            else:
                a = cli.get(base + "/auth/me", headers=h)
                good = a.status_code == 200
                print("  %-28s /auth/me=%s" % (email, a.status_code))

            ok = ok and good

    print("\n%s" % ("All demo accounts work." if ok
                    else "Some accounts still failing."))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())