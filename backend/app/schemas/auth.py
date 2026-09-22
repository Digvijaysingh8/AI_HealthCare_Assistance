from pydantic import BaseModel


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    age: int
    gender: str
    role: str = "patient"


class LoginRequest(BaseModel):
    email: str
    password: str