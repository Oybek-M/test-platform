from pydantic import BaseModel, field_validator


class GroupCreate(BaseModel):
    course_id: int
    name: str

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name cannot be blank")
        return v


class GroupUpdate(BaseModel):
    name: str | None = None

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("name cannot be blank")
        return v


class GroupOut(BaseModel):
    id: int
    course_id: int
    name: str

    model_config = {"from_attributes": True}
