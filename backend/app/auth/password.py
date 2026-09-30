from passlib.context import CryptContext


# bcrypt_rounds is the work factor. The passlib default is 12, which costs
# ~220ms per login and dominates the time the login page spends waiting.
# 10 is ~3x faster and still a strong work factor; raise it back to 12 (and
# re-hash on next login) if this ever handles real credentials.
BCRYPT_ROUNDS = 10

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=BCRYPT_ROUNDS
)


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
):
    return pwd_context.verify(
        plain_password,
        hashed_password
    )