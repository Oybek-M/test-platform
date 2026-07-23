from pydantic import BaseModel


class StudentTextImportRequest(BaseModel):
    text: str


class StudentOut(BaseModel):
    id: int
    group_id: int
    full_name: str

    model_config = {"from_attributes": True}


class StudentImportResult(BaseModel):
    created: list[StudentOut]
    warnings: list[str]
