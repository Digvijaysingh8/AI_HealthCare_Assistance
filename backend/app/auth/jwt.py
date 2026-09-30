
import os
import secrets
from datetime import datetime, timedelta, timezone

from jose import jwt
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

# A missing SECRET_KEY used to raise here, which killed the process during
# import -- before uvicorn ever bound a port. On a host like Render that
# surfaces only as "no open ports detected", with the real cause buried in
# the log. Generate a throwaway key instead so the service still starts and
# the misconfiguration is visible in the logs and from /health.
if not SECRET_KEY or SECRET_KEY == "change-this-secret-key":
    SECRET_KEY = secrets.token_urlsafe(48)

    width = 66
    lines = [
        "WARNING: SECRET_KEY is not set.",
        "",
        "Using a random key generated for this process only.",
        "Every restart invalidates all existing login tokens, and",
        "separate instances cannot verify each other's.",
        "",
        "Set SECRET_KEY in the environment before going live.",
    ]
    print(
        "\n"
        + "\n".join(
            ["#" * width]
            + [("# %s" % line).ljust(width - 1) + "#" for line in lines]
            + ["#" * width]
        )
        + "\n",
        flush=True,
    )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def verify_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except Exception:
        return None