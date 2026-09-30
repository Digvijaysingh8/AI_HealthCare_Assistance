from pydantic import BaseModel


class DoctorCreate(BaseModel):
    name: str
    specialization: str
    user_id: int | None = None


class DoctorUpdate(BaseModel):
    name: str
    specialization: str