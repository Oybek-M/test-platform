from pydantic import BaseModel, field_validator


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminOut(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}


class ProfileUpdateRequest(BaseModel):
    current_password: str
    new_username: str | None = None
    new_password: str | None = None

    @field_validator("new_username")
    @classmethod
    def username_not_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("new_username cannot be blank")
        return v

    @field_validator("new_password")
    @classmethod
    def password_not_blank(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("new_password cannot be blank")
        return v
