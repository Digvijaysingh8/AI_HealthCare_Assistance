from pydantic import BaseModel
from datetime import date, time


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time


class AppointmentUpdate(BaseModel):
    patient_id: int
    doctor_id: int
    appointment_date: date
    appointment_time: time

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    patient_name: str
    doctor_id: int
    doctor_name: str
    appointment_date: date
    appointment_time: time