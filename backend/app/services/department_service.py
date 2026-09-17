from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.department import Department
from app.schemas.department import DepartmentCreate, DepartmentUpdate


def create_department(
    department: DepartmentCreate,
    session: Session
):
    new_department = Department(
        name=department.name
    )

    session.add(new_department)
    session.commit()
    session.refresh(new_department)

    return new_department

def get_departments(
    session: Session 
):
    departments = session.exec(
        select(Department)
    ).all()

    return departments

def get_department(
    department_id: int,
    session: Session 
):
    department = session.get(Department, department_id)
    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return department

def update_department(
    department_id: int,
    updated_department: DepartmentUpdate,
    session: Session 
):
    department = session.get(Department, department_id)

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    department.name = updated_department.name

    session.add(department)
    session.commit()
    session.refresh(department)

    return department

def delete_department(
    department_id: int,
    session: Session 
):
    department = session.get(Department, department_id)

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    session.delete(department)
    session.commit()

    return {"message": "Department deleted successfully"}