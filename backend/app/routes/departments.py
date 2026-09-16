from fastapi import APIRouter, Depends,HTTPException
from sqlmodel import Session, select

from app.models.department import Department
from app.database.session import get_session
from app.schemas.department import DepartmentCreate, DepartmentUpdate


router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)


@router.post("/")
def create_department(
    department: DepartmentCreate,
    session: Session = Depends(get_session)
):
    new_department = Department(
        name=department.name
    )
    session.add(new_department)
    session.commit()
    session.refresh(new_department)

    return new_department


@router.get("/")
def get_departments(
    session: Session = Depends(get_session)
):
    departments = session.exec(
        select(Department)
    ).all()

    return departments


@router.get("/{department_id}")
def get_department(
    department_id: int,
    session: Session = Depends(get_session)
):
    department = session.get(Department, department_id)
    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department not found"
        )

    return department


@router.put("/{department_id}")
def update_department(
    department_id: int,
    updated_department: DepartmentUpdate,
    session: Session = Depends(get_session)
):
    department = session.get(Department, department_id)

    if not department:
        return {"message": "Department not found"}

    department.name = updated_department.name

    session.add(department)
    session.commit()
    session.refresh(department)

    return department


@router.delete("/{department_id}")
def delete_department(
    department_id: int,
    session: Session = Depends(get_session)
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