from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.mixins import SoftDeleteMixin


class Exam(SoftDeleteMixin, Base):
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    question_count: Mapped[int] = mapped_column(Integer, nullable=False)

    shuffle_questions: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    shuffle_options: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    allow_resume: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    show_result_to_student: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    totp_secret: Mapped[str] = mapped_column(String(64), nullable=False)
    totp_digits: Mapped[int] = mapped_column(Integer, default=6, nullable=False)
    totp_period: Mapped[int] = mapped_column(Integer, default=30, nullable=False)

    status: Mapped[str] = mapped_column(String(20), default="draft", nullable=False)
    access_code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
