from fastapi import APIRouter, Depends,HTTPException
from sqlmodel import Session, select
from app.services import department_service
from app.models.department import Department
from app.database.session import get_session
from app.schemas.department import DepartmentCreate, DepartmentUpdate
from app.auth.dependencies import require_role
from app.models.user import User

router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)


@router.post("/")
def create_department(
    department: DepartmentCreate,
        current_user: User = Depends(
        require_role(["admin"])
    ),
    session: Session = Depends(get_session)
):
    return department_service.create_department(
        department,
        session
    )


@router.get("/")
def get_departments(
    session: Session = Depends(get_session)
):
    return department_service.get_departments(
        session
    )


@router.get("/{department_id}")
def get_department(
    department_id: int,
    session: Session = Depends(get_session)
):
    return department_service.get_department(
        department_id,
        session
    )


@router.put("/{department_id}")
def update_department(
    department_id: int,
    updated_department: DepartmentUpdate,
    current_user: User = Depends(
        require_role(["admin"])
    ),
    session: Session = Depends(get_session)
):
    return department_service.update_department(
        department_id,
        updated_department,
        session
    )


@router.delete("/{department_id}")
def delete_department(
    department_id: int,
    current_user: User = Depends(
        require_role(["admin"])
    ),
    session: Session = Depends(get_session)
):
    return department_service.delete_department(
        department_id,
        session 
    )