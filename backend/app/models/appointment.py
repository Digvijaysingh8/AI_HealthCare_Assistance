from typing import Optional

from sqlmodel import SQLModel, Field


class Appointment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int
    doctor_id: int
    appointment_date: str
    appointment_time: str