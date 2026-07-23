from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.database import get_db
from app.models.course import Course
from app.models.question import Question
from app.schemas.question import (
    QuestionCreate,
    QuestionImportPreview,
    QuestionImportResult,
    QuestionOut,
    QuestionUpdate,
)
from app.services.imports import parse_questions_xlsx

router = APIRouter(prefix="/api/admin", tags=["admin-questions"], dependencies=[Depends(get_current_admin)])

SAMPLES_DIR = Path(__file__).resolve().parent.parent.parent / "templates" / "samples"


def _get_course_or_404(course_id: int, db: Session) -> Course:
    course = db.query(Course).filter(Course.id == course_id, Course.is_deleted.is_(False)).first()
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


def _get_question_or_404(course_id: int, question_id: int, db: Session) -> Question:
    question = (
        db.query(Question)
        .filter(Question.id == question_id, Question.course_id == course_id, Question.is_deleted.is_(False))
        .first()
    )
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return question


@router.get("/courses/{course_id}/questions", response_model=list[QuestionOut])
def list_questions(
    course_id: int,
    topic: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
):
    _get_course_or_404(course_id, db)
    query = db.query(Question).filter(Question.course_id == course_id, Question.is_deleted.is_(False))
    if topic is not None:
        query = query.filter(Question.topic == topic)
    if is_active is not None:
        query = query.filter(Question.is_active == is_active)
    return query.order_by(Question.id).all()


@router.post("/courses/{course_id}/questions", response_model=QuestionOut, status_code=status.HTTP_201_CREATED)
def create_question(course_id: int, payload: QuestionCreate, db: Session = Depends(get_db)):
    _get_course_or_404(course_id, db)
    question = Question(
        course_id=course_id,
        text=payload.text,
        options=payload.options,
        correct_index=payload.correct_index,
        topic=payload.topic,
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


@router.put("/courses/{course_id}/questions/{question_id}", response_model=QuestionOut)
def update_question(course_id: int, question_id: int, payload: QuestionUpdate, db: Session = Depends(get_db)):
    question = _get_question_or_404(course_id, question_id, db)

    new_options = payload.options if payload.options is not None else question.options
    new_correct_index = payload.correct_index if payload.correct_index is not None else question.correct_index
    if not (0 <= new_correct_index < len(new_options)):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="correct_index out of range")

    if payload.text is not None:
        question.text = payload.text
    question.options = new_options
    question.correct_index = new_correct_index
    if payload.topic is not None:
        question.topic = payload.topic
    if payload.is_active is not None:
        question.is_active = payload.is_active

    db.commit()
    db.refresh(question)
    return question


@router.delete("/courses/{course_id}/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(course_id: int, question_id: int, db: Session = Depends(get_db)):
    question = _get_question_or_404(course_id, question_id, db)
    question.is_deleted = True
    db.commit()


@router.post("/courses/{course_id}/questions/import")
async def import_questions(
    course_id: int,
    file: UploadFile = File(...),
    confirm: bool = Form(False),
    db: Session = Depends(get_db),
):
    _get_course_or_404(course_id, db)
    content = await file.read()
    result = parse_questions_xlsx(content)

    if result["errors"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"questions_found": len(result["questions"]), "errors": result["errors"]},
        )

    if not confirm:
        return QuestionImportPreview(
            questions_found=len(result["questions"]),
            errors=[],
            preview=result["questions"],
        )

    created = []
    for q in result["questions"]:
        question = Question(
            course_id=course_id,
            text=q["text"],
            options=q["options"],
            correct_index=q["correct_index"],
            topic=q["topic"],
        )
        db.add(question)
        created.append(question)
    db.commit()
    return QuestionImportResult(imported=len(created))


@router.get("/samples/questions.xlsx")
def download_questions_sample():
    file_path = SAMPLES_DIR / "questions_template.xlsx"
    return FileResponse(
        path=file_path,
        filename="questions_template.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
