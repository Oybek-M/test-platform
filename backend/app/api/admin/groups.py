from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.database import get_db
from app.models.group import Group
from app.models.student import Student
from app.schemas.group import GroupCreate, GroupOut, GroupUpdate
from app.schemas.student import StudentImportResult, StudentOut, StudentTextImportRequest
from app.services.imports import parse_students_text, parse_students_xlsx

router = APIRouter(prefix="/api/admin", tags=["admin-groups"], dependencies=[Depends(get_current_admin)])

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "templates" / "samples"


def _get_group_or_404(group_id: int, db: Session) -> Group:
    group = db.query(Group).filter(Group.id == group_id, Group.is_deleted.is_(False)).first()
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    return group


def _persist_students(group_id: int, names: list[str], warnings: list[str], db: Session) -> StudentImportResult:
    created = []
    for name in names:
        student = Student(group_id=group_id, full_name=name)
        db.add(student)
        created.append(student)
    db.commit()
    for student in created:
        db.refresh(student)
    return StudentImportResult(created=created, warnings=warnings)


@router.get("/groups", response_model=list[GroupOut])
def list_groups(course_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Group).filter(Group.is_deleted.is_(False))
    if course_id is not None:
        query = query.filter(Group.course_id == course_id)
    return query.order_by(Group.id).all()


@router.post("/groups", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
def create_group(payload: GroupCreate, db: Session = Depends(get_db)):
    group = Group(course_id=payload.course_id, name=payload.name)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


@router.get("/groups/{group_id}", response_model=GroupOut)
def get_group(group_id: int, db: Session = Depends(get_db)):
    return _get_group_or_404(group_id, db)


@router.put("/groups/{group_id}", response_model=GroupOut)
def update_group(group_id: int, payload: GroupUpdate, db: Session = Depends(get_db)):
    group = _get_group_or_404(group_id, db)
    if payload.name is not None:
        group.name = payload.name
    db.commit()
    db.refresh(group)
    return group


@router.delete("/groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(group_id: int, db: Session = Depends(get_db)):
    group = _get_group_or_404(group_id, db)
    group.is_deleted = True
    db.commit()


@router.get("/groups/{group_id}/students", response_model=list[StudentOut])
def list_students(group_id: int, db: Session = Depends(get_db)):
    _get_group_or_404(group_id, db)
    return (
        db.query(Student)
        .filter(Student.group_id == group_id, Student.is_deleted.is_(False))
        .order_by(Student.id)
        .all()
    )


@router.post("/groups/{group_id}/students", response_model=StudentImportResult, status_code=status.HTTP_201_CREATED)
def add_students_from_text(group_id: int, payload: StudentTextImportRequest, db: Session = Depends(get_db)):
    _get_group_or_404(group_id, db)
    result = parse_students_text(payload.text)
    return _persist_students(group_id, result["students"], result["warnings"], db)


@router.post(
    "/groups/{group_id}/students/import",
    response_model=StudentImportResult,
    status_code=status.HTTP_201_CREATED,
)
async def add_students_from_xlsx(group_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    _get_group_or_404(group_id, db)
    content = await file.read()
    result = parse_students_xlsx(content)
    return _persist_students(group_id, result["students"], result["warnings"], db)


@router.get("/samples/students.xlsx")
def download_students_sample():
    file_path = SAMPLES_DIR / "students_template.xlsx"
    return FileResponse(
        path=file_path,
        filename="students_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
