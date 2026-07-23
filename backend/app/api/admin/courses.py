from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.database import get_db
from app.models.course import DEFAULT_GRADING_SCALE, Course
from app.schemas.course import CourseCreate, CourseOut, CourseUpdate

router = APIRouter(
    prefix="/api/admin/courses",
    tags=["admin-courses"],
    dependencies=[Depends(get_current_admin)],
)


def _get_course_or_404(course_id: int, db: Session) -> Course:
    course = (
        db.query(Course)
        .filter(Course.id == course_id, Course.is_deleted.is_(False))
        .first()
    )
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.get("", response_model=list[CourseOut])
def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).filter(Course.is_deleted.is_(False)).order_by(Course.id).all()


@router.post("", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(payload: CourseCreate, db: Session = Depends(get_db)):
    course = Course(
        name=payload.name,
        description=payload.description,
        grading_scale=payload.grading_scale or DEFAULT_GRADING_SCALE,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    return _get_course_or_404(course_id, db)


@router.put("/{course_id}", response_model=CourseOut)
def update_course(course_id: int, payload: CourseUpdate, db: Session = Depends(get_db)):
    course = _get_course_or_404(course_id, db)
    if payload.name is not None:
        course.name = payload.name
    if payload.description is not None:
        course.description = payload.description
    if payload.grading_scale is not None:
        course.grading_scale = payload.grading_scale
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    course = _get_course_or_404(course_id, db)
    course.is_deleted = True
    db.commit()
