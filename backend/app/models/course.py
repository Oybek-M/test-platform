from sqlalchemy import JSON, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.mixins import SoftDeleteMixin

DEFAULT_GRADING_SCALE = [
    {"grade": "A", "min": 90},
    {"grade": "B", "min": 80},
    {"grade": "C", "min": 70},
    {"grade": "D", "min": 60},
    {"grade": "F", "min": 0},
]


class Course(SoftDeleteMixin, Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    grading_scale: Mapped[list] = mapped_column(JSON, default=lambda: DEFAULT_GRADING_SCALE)
