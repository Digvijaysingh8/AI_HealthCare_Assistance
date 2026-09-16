from pydantic import BaseModel


class DepartmentCreate(BaseModel):
    name: str

class DepartmentUpdate(BaseModel):
    name: str