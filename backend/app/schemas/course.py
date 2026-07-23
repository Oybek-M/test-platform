from pydantic import BaseModel, field_validator

from app.models.course import DEFAULT_GRADING_SCALE


class GradeBand(BaseModel):
    grade: str
    min: int


def _validate_scale(scale: list[dict]) -> list[dict]:
    if not scale:
        raise ValueError("grading_scale must have at least one band")
    for band in scale:
        if "grade" not in band or "min" not in band:
            raise ValueError("each grading_scale item needs 'grade' and 'min'")
        if not (0 <= band["min"] <= 100):
            raise ValueError("grading_scale 'min' must be between 0 and 100")
    return scale


class CourseCreate(BaseModel):
    name: str
    description: str | None = None
    grading_scale: list[dict] | None = None

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name cannot be blank")
        return v

    @field_validator("grading_scale")
    @classmethod
    def validate_scale(cls, v):
        if v is None:
            return v
        return _validate_scale(v)


class CourseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    grading_scale: list[dict] | None = None

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("name cannot be blank")
        return v

    @field_validator("grading_scale")
    @classmethod
    def validate_scale(cls, v):
        if v is None:
            return v
        return _validate_scale(v)


class CourseOut(BaseModel):
    id: int
    name: str
    description: str | None
    grading_scale: list[dict]

    model_config = {"from_attributes": True}
