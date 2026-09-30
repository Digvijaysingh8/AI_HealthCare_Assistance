import os

from dotenv import load_dotenv
from sqlmodel import SQLModel, create_engine
from sqlalchemy.engine import make_url

from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.department import Department
from app.models.appointment import Appointment
from app.models.user import User

# Load .env before reading DATABASE_URI, otherwise the URI is missing at
# import time and we silently fall back to the local SQLite file.
load_dotenv()

DEFAULT_SQLITE_URL = "sqlite:///healthcare.db"

# Driver options that belong to the mysql CLI / connectors, not to SQLAlchemy.
# SQLAlchemy forwards unknown query params straight to the DBAPI connect()
# call, so PyMySQL rejects them (e.g. `?ssl-mode=REQUIRED`).
UNSUPPORTED_QUERY_PARAMS = {"ssl-mode", "ssl_mode"}


def _build_database_uri(raw_uri: str) -> str:
    """Normalise a .env DATABASE_URI into something SQLAlchemy can open."""
    uri = raw_uri.strip()

    # Use PyMySQL for MySQL connections.
    if uri.startswith("mysql://"):
        uri = uri.replace("mysql://", "mysql+pymysql://", 1)

    url = make_url(uri)

    query = dict(url.query)
    for key in list(query):
        if key.lower() in UNSUPPORTED_QUERY_PARAMS:
            # TLS is negotiated by PyMySQL itself; see _resolve_database_url.
            query.pop(key)

    return url.set(query=query).render_as_string(hide_password=False)


def _resolve_database_url():
    raw_uri = os.getenv("DATABASE_URI")

    if not raw_uri or not raw_uri.strip():
        # Local development fallback
        return DEFAULT_SQLITE_URL, {"check_same_thread": False}

    uri = _build_database_uri(raw_uri)

    connect_args = {}
    if make_url(uri).get_backend_name() == "mysql":
        # PyMySQL enables TLS automatically. Hostname checking is off because
        # managed MySQL providers (Aiven, RDS, ...) issue certificates under
        # their own CN, not the connection hostname.
        connect_args["ssl"] = {"check_hostname": False}

    return uri, connect_args


DATABASE_URL, CONNECT_ARGS = _resolve_database_url()

_safe_url = DATABASE_URL.split("@")[-1]
print("Using database:", _safe_url if DATABASE_URL != DEFAULT_SQLITE_URL else "SQLite", flush=True)


engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args=CONNECT_ARGS,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)