from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.database import get_db
from app.models.attempt import Attempt
from app.models.course import Course
from app.models.exam import Exam
from app.models.group import Group
from app.models.question import Question
from app.models.student import Student
from app.schemas.exam import (
    AttemptResultOut,
    ExamCreate,
    ExamOut,
    ExamStatusUpdate,
    ExamTotpOut,
    ExamUpdate,
)
from app.services import access_code as access_code_service
from app.services import totp

router = APIRouter(prefix="/api/admin/exams", tags=["admin-exams"], dependencies=[Depends(get_current_admin)])


def _get_exam_or_404(exam_id: int, db: Session) -> Exam:
    exam = db.query(Exam).filter(Exam.id == exam_id, Exam.is_deleted.is_(False)).first()
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
    return exam


def _active_question_count(course_id: int, db: Session) -> int:
    return (
        db.query(Question)
        .filter(Question.course_id == course_id, Question.is_active.is_(True), Question.is_deleted.is_(False))
        .count()
    )


def _unique_access_code(db: Session) -> str:
    for _ in range(10):
        code = access_code_service.generate()
        exists = db.query(Exam).filter(Exam.access_code == code).first()
        if exists is None:
            return code
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not generate unique access code")


@router.get("", response_model=list[ExamOut])
def list_exams(
    course_id: int | None = None,
    group_id: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Exam).filter(Exam.is_deleted.is_(False))
    if course_id is not None:
        query = query.filter(Exam.course_id == course_id)
    if group_id is not None:
        query = query.filter(Exam.group_id == group_id)
    return query.order_by(Exam.id).all()


@router.post("", response_model=ExamOut, status_code=status.HTTP_201_CREATED)
def create_exam(payload: ExamCreate, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == payload.course_id, Course.is_deleted.is_(False)).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    group = db.query(Group).filter(Group.id == payload.group_id, Group.is_deleted.is_(False)).first()
    if group is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    available = _active_question_count(payload.course_id, db)
    if payload.question_count > available:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"question_count ({payload.question_count}) exceeds active questions available ({available})",
        )

    exam = Exam(
        course_id=payload.course_id,
        group_id=payload.group_id,
        title=payload.title,
        starts_at=payload.starts_at,
        duration_minutes=payload.duration_minutes,
        question_count=payload.question_count,
        shuffle_questions=payload.shuffle_questions,
        shuffle_options=payload.shuffle_options,
        allow_resume=payload.allow_resume,
        show_result_to_student=payload.show_result_to_student,
        totp_secret=totp.new_secret(),
        totp_digits=payload.totp_digits,
        totp_period=payload.totp_period,
        status="draft",
        access_code=_unique_access_code(db),
    )
    db.add(exam)
    db.commit()
    db.refresh(exam)
    return exam


@router.get("/{exam_id}", response_model=ExamOut)
def get_exam(exam_id: int, db: Session = Depends(get_db)):
    return _get_exam_or_404(exam_id, db)


@router.put("/{exam_id}", response_model=ExamOut)
def update_exam(exam_id: int, payload: ExamUpdate, db: Session = Depends(get_db)):
    exam = _get_exam_or_404(exam_id, db)

    new_question_count = payload.question_count if payload.question_count is not None else exam.question_count
    available = _active_question_count(exam.course_id, db)
    if new_question_count > available:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"question_count ({new_question_count}) exceeds active questions available ({available})",
        )

    for field in (
        "title",
        "starts_at",
        "duration_minutes",
        "question_count",
        "shuffle_questions",
        "shuffle_options",
        "allow_resume",
        "show_result_to_student",
        "totp_digits",
        "totp_period",
    ):
        value = getattr(payload, field)
        if value is not None:
            setattr(exam, field, value)

    db.commit()
    db.refresh(exam)
    return exam


@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam(exam_id: int, db: Session = Depends(get_db)):
    exam = _get_exam_or_404(exam_id, db)
    exam.is_deleted = True
    db.commit()


@router.post("/{exam_id}/status", response_model=ExamOut)
def update_exam_status(exam_id: int, payload: ExamStatusUpdate, db: Session = Depends(get_db)):
    exam = _get_exam_or_404(exam_id, db)
    exam.status = payload.status
    db.commit()
    db.refresh(exam)
    return exam


@router.get("/{exam_id}/totp", response_model=ExamTotpOut)
def get_live_totp_code(exam_id: int, db: Session = Depends(get_db)):
    exam = _get_exam_or_404(exam_id, db)
    code, seconds_left = totp.current_code(exam.totp_secret, exam.totp_digits, exam.totp_period)
    return ExamTotpOut(code=code, seconds_left=seconds_left)


@router.get("/{exam_id}/results", response_model=list[AttemptResultOut])
def get_exam_results(exam_id: int, db: Session = Depends(get_db)):
    exam = _get_exam_or_404(exam_id, db)
    attempts = db.query(Attempt).filter(Attempt.exam_id == exam.id).order_by(Attempt.id).all()

    results = []
    for attempt in attempts:
        student = db.get(Student, attempt.student_id)
        results.append(
            AttemptResultOut(
                student_id=attempt.student_id,
                student_name=student.full_name if student else "?",
                score=attempt.score,
                total=attempt.total,
                percent=attempt.percent,
                grade=attempt.grade,
                started_at=attempt.started_at,
                submitted_at=attempt.submitted_at,
                status=attempt.status,
            )
        )
    return results
