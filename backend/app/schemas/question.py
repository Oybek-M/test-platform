from pydantic import BaseModel, field_validator, model_validator


class QuestionCreate(BaseModel):
    text: str
    options: list[str]
    correct_index: int
    topic: str | None = None

    @field_validator("text")
    @classmethod
    def text_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("text cannot be blank")
        return v

    @field_validator("options")
    @classmethod
    def options_len(cls, v: list[str]) -> list[str]:
        if not (2 <= len(v) <= 6):
            raise ValueError("options must contain between 2 and 6 items")
        return v

    @model_validator(mode="after")
    def correct_index_in_range(self):
        if not (0 <= self.correct_index < len(self.options)):
            raise ValueError("correct_index out of range for options")
        return self


class QuestionUpdate(BaseModel):
    text: str | None = None
    options: list[str] | None = None
    correct_index: int | None = None
    topic: str | None = None
    is_active: bool | None = None

    @field_validator("options")
    @classmethod
    def options_len(cls, v: list[str] | None) -> list[str] | None:
        if v is not None and not (2 <= len(v) <= 6):
            raise ValueError("options must contain between 2 and 6 items")
        return v


class QuestionOut(BaseModel):
    id: int
    course_id: int
    text: str
    options: list[str]
    correct_index: int
    topic: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class QuestionImportPreview(BaseModel):
    questions_found: int
    errors: list[str]
    preview: list[dict]


class QuestionImportResult(BaseModel):
    imported: int
