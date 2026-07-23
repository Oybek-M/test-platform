from datetime import datetime

from pydantic import BaseModel


class ExamPublicStatus(BaseModel):
    title: str
    group_name: str
    status: str
    starts_at: datetime
    duration_minutes: int
    is_open_now: bool


class VerifyCodeRequest(BaseModel):
    code: str


class VerifyCodeResponse(BaseModel):
    ok: bool


class StudentPublicOut(BaseModel):
    id: int
    full_name: str

    model_config = {"from_attributes": True}


class StartExamRequest(BaseModel):
    student_id: int
    code: str


class PublicQuestionOut(BaseModel):
    id: int
    text: str
    options: list[str]


class StartExamResponse(BaseModel):
    attempt_id: int
    ends_at: datetime
    questions: list[PublicQuestionOut]


class SubmitExamRequest(BaseModel):
    attempt_id: int
    answers: dict[int, int]
