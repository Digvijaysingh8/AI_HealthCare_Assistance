from pydantic import BaseModel


class DoctorCreate(BaseModel):
    name: str
    specialization: str

class DoctorUpdate(BaseModel):
    name: str
    specialization: str    