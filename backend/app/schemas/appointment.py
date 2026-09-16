from pydantic import BaseModel

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: str
    appointment_time: str

class AppointmentUpdate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: str
    appointment_time: str    