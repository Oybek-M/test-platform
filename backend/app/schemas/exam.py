from datetime import datetime

from pydantic import BaseModel, field_validator

VALID_STATUSES = {"draft", "scheduled", "open", "closed"}


class ExamCreate(BaseModel):
    course_id: int
    group_id: int
    title: str
    starts_at: datetime
    duration_minutes: int
    question_count: int
    shuffle_questions: bool = True
    shuffle_options: bool = True
    allow_resume: bool = False
    show_result_to_student: bool = True
    totp_digits: int = 6
    totp_period: int = 30

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title cannot be blank")
        return v

    @field_validator("duration_minutes")
    @classmethod
    def duration_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("duration_minutes must be positive")
        return v

    @field_validator("question_count")
    @classmethod
    def question_count_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("question_count must be positive")
        return v

    @field_validator("totp_digits")
    @classmethod
    def digits_valid(cls, v: int) -> int:
        if v not in (4, 6):
            raise ValueError("totp_digits must be 4 or 6")
        return v

    @field_validator("totp_period")
    @classmethod
    def period_valid(cls, v: int) -> int:
        if v not in (30, 60):
            raise ValueError("totp_period must be 30 or 60")
        return v


class ExamUpdate(BaseModel):
    title: str | None = None
    starts_at: datetime | None = None
    duration_minutes: int | None = None
    question_count: int | None = None
    shuffle_questions: bool | None = None
    shuffle_options: bool | None = None
    allow_resume: bool | None = None
    show_result_to_student: bool | None = None
    totp_digits: int | None = None
    totp_period: int | None = None

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("title cannot be blank")
        return v

    @field_validator("duration_minutes")
    @classmethod
    def duration_positive(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("duration_minutes must be positive")
        return v

    @field_validator("question_count")
    @classmethod
    def question_count_positive(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("question_count must be positive")
        return v

    @field_validator("totp_digits")
    @classmethod
    def digits_valid(cls, v: int | None) -> int | None:
        if v is not None and v not in (4, 6):
            raise ValueError("totp_digits must be 4 or 6")
        return v

    @field_validator("totp_period")
    @classmethod
    def period_valid(cls, v: int | None) -> int | None:
        if v is not None and v not in (30, 60):
            raise ValueError("totp_period must be 30 or 60")
        return v


class ExamStatusUpdate(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def status_valid(cls, v: str) -> str:
        if v not in VALID_STATUSES:
            raise ValueError(f"status must be one of {sorted(VALID_STATUSES)}")
        return v


class ExamOut(BaseModel):
    id: int
    course_id: int
    group_id: int
    title: str
    starts_at: datetime
    duration_minutes: int
    question_count: int
    shuffle_questions: bool
    shuffle_options: bool
    allow_resume: bool
    show_result_to_student: bool
    totp_digits: int
    totp_period: int
    status: str
    access_code: str

    model_config = {"from_attributes": True}


class ExamTotpOut(BaseModel):
    code: str
    seconds_left: int


class AttemptResultOut(BaseModel):
    student_id: int
    student_name: str
    score: int | None
    total: int | None
    percent: int | None
    grade: str | None
    started_at: datetime
    submitted_at: datetime | None
    status: str
