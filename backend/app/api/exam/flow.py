from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.attempt import Attempt
from app.models.course import Course
from app.models.exam import Exam
from app.models.group import Group
from app.models.question import Question
from app.models.student import Student
from app.schemas.exam_public import (
    ExamPublicStatus,
    PublicQuestionOut,
    StartExamRequest,
    StartExamResponse,
    StudentPublicOut,
    SubmitExamRequest,
    VerifyCodeRequest,
    VerifyCodeResponse,
)
from app.services import exam_engine, grading, totp

router = APIRouter(prefix="/api/exam", tags=["exam-flow"])


def _get_exam_by_code_or_404(access_code: str, db: Session) -> Exam:
    exam = db.query(Exam).filter(Exam.access_code == access_code, Exam.is_deleted.is_(False)).first()
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")
    return exam


def _as_aware_utc(dt: datetime) -> datetime:
    # Some backends (e.g. SQLite, used in tests) don't round-trip tzinfo even though the
    # column is declared timezone-aware; treat any naive value as UTC rather than crash.
    return dt if dt.tzinfo is not None else dt.replace(tzinfo=timezone.utc)


def _is_open_now(exam: Exam) -> bool:
    # Entry is gated purely by starts_at + the admin-controlled open/closed status - there is
    # no fixed global end time. Each student's own deadline is their personal started_at +
    # duration (see /start, /submit), so a student who enters late still gets the full
    # duration instead of having it silently truncated by a shared window.
    if exam.status != "open":
        return False
    return _as_aware_utc(exam.starts_at) <= datetime.now(timezone.utc)


def _attempt_deadline(exam: Exam, attempt: Attempt) -> datetime:
    return _as_aware_utc(attempt.started_at) + timedelta(minutes=exam.duration_minutes)


def _verify_or_403(exam: Exam, code: str) -> None:
    if not totp.verify_code(exam.totp_secret, code, exam.totp_digits, exam.totp_period):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid code")


def _to_public_questions(snapshot: list[dict]) -> list[PublicQuestionOut]:
    return [PublicQuestionOut(id=q["id"], text=q["text"], options=q["options"]) for q in snapshot]


@router.get("/{access_code}", response_model=ExamPublicStatus)
def get_exam_status(access_code: str, db: Session = Depends(get_db)):
    exam = _get_exam_by_code_or_404(access_code, db)
    group = db.get(Group, exam.group_id)
    return ExamPublicStatus(
        title=exam.title,
        group_name=group.name if group else "",
        status=exam.status,
        starts_at=exam.starts_at,
        duration_minutes=exam.duration_minutes,
        is_open_now=_is_open_now(exam),
    )


@router.post("/{access_code}/verify-code", response_model=VerifyCodeResponse)
def verify_code(access_code: str, payload: VerifyCodeRequest, db: Session = Depends(get_db)):
    exam = _get_exam_by_code_or_404(access_code, db)
    _verify_or_403(exam, payload.code)
    return VerifyCodeResponse(ok=True)


@router.get("/{access_code}/students", response_model=list[StudentPublicOut])
def list_available_students(access_code: str, code: str, db: Session = Depends(get_db)):
    exam = _get_exam_by_code_or_404(access_code, db)
    _verify_or_403(exam, code)

    students = (
        db.query(Student)
        .filter(Student.group_id == exam.group_id, Student.is_deleted.is_(False))
        .order_by(Student.full_name)
        .all()
    )

    blocked_ids: set[int] = set()
    if not exam.allow_resume:
        finished = (
            db.query(Attempt)
            .filter(Attempt.exam_id == exam.id, Attempt.status.in_(["submitted", "expired"]))
            .all()
        )
        blocked_ids = {a.student_id for a in finished}

    return [s for s in students if s.id not in blocked_ids]


@router.post("/{access_code}/start", response_model=StartExamResponse)
def start_exam(access_code: str, payload: StartExamRequest, db: Session = Depends(get_db)):
    exam = _get_exam_by_code_or_404(access_code, db)
    _verify_or_403(exam, payload.code)

    student = (
        db.query(Student)
        .filter(Student.id == payload.student_id, Student.group_id == exam.group_id, Student.is_deleted.is_(False))
        .first()
    )
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not in this exam's group")

    existing = (
        db.query(Attempt).filter(Attempt.exam_id == exam.id, Attempt.student_id == student.id).first()
    )

    if existing is not None and existing.status in ("submitted", "expired"):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Attempt already completed")

    if existing is not None and existing.status == "in_progress":
        # Resuming an already-started attempt (e.g. after a page reload) must not be blocked
        # by the admin closing the exam to new entries - the student already has their own
        # deadline (started_at + duration) and should be able to finish it regardless.
        attempt = existing
    else:
        if not _is_open_now(exam):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Exam is not open right now")
        active_questions = (
            db.query(Question)
            .filter(Question.course_id == exam.course_id, Question.is_active.is_(True), Question.is_deleted.is_(False))
            .all()
        )
        pool = [
            {"id": q.id, "text": q.text, "options": q.options, "correct_index": q.correct_index}
            for q in active_questions
        ]
        snapshot = exam_engine.pick_questions(
            pool, exam.question_count, exam.shuffle_questions, exam.shuffle_options
        )
        attempt = Attempt(
            exam_id=exam.id,
            student_id=student.id,
            started_at=datetime.now(timezone.utc),
            question_ids=[q["id"] for q in snapshot],
            question_snapshot=snapshot,
            answers={},
            status="in_progress",
        )
        db.add(attempt)
        db.commit()
        db.refresh(attempt)

    ends_at = _attempt_deadline(exam, attempt)
    return StartExamResponse(
        attempt_id=attempt.id,
        ends_at=ends_at,
        questions=_to_public_questions(attempt.question_snapshot),
    )


@router.post("/{access_code}/submit")
def submit_exam(access_code: str, payload: SubmitExamRequest, db: Session = Depends(get_db)):
    exam = _get_exam_by_code_or_404(access_code, db)
    attempt = db.query(Attempt).filter(Attempt.id == payload.attempt_id, Attempt.exam_id == exam.id).first()
    if attempt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    if attempt.status != "in_progress":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Attempt already submitted")

    now = datetime.now(timezone.utc)
    deadline = _attempt_deadline(exam, attempt)
    expired = now > deadline

    score, total = exam_engine.grade_attempt(attempt.question_snapshot, payload.answers)
    percent = grading.calc_percent(score, total)
    course = db.get(Course, exam.course_id)
    grade = grading.calc_grade(percent, course.grading_scale)

    attempt.answers = {str(k): v for k, v in payload.answers.items()}
    attempt.score = score
    attempt.total = total
    attempt.percent = percent
    attempt.grade = grade
    attempt.submitted_at = now
    attempt.status = "expired" if expired else "submitted"
    db.commit()

    if exam.show_result_to_student:
        return {"score": score, "total": total, "percent": percent, "grade": grade}
    return {"submitted": True}
