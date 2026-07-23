from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.mixins import SoftDeleteMixin


class Attempt(SoftDeleteMixin, Base):
    __tablename__ = "attempts"
    __table_args__ = (UniqueConstraint("exam_id", "student_id", name="uq_attempt_exam_student"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)

    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    question_ids: Mapped[list] = mapped_column(JSON, nullable=False)
    # Per-attempt presented question snapshot: [{"id","text","options","correct_index"}, ...].
    # Stored because shuffle_options may reorder options per-attempt, changing which index is
    # correct - grading must use THIS snapshot's correct_index, not the master Question row.
    question_snapshot: Mapped[list] = mapped_column(JSON, nullable=False)
    answers: Mapped[dict] = mapped_column(JSON, default=dict)

    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    percent: Mapped[int | None] = mapped_column(Integer, nullable=True)
    grade: Mapped[str | None] = mapped_column(String(5), nullable=True)

    status: Mapped[str] = mapped_column(String(20), default="in_progress", nullable=False)
