from typing import Optional

from sqlmodel import SQLModel, Field


class Patient(SQLModel, table=True):

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    user_id: Optional[int] = Field(
        default=None,
        index=True
    )

    name: str

    age: int

    gender: str