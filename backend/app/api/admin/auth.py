from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.config import settings
from app.core.security import create_token, hash_password, verify_password
from app.database import get_db
from app.models.admin import Admin
from app.schemas.auth import AdminOut, LoginRequest, ProfileUpdateRequest, TokenResponse

router = APIRouter(prefix="/api/admin/auth", tags=["admin-auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == payload.username).first()
    if admin is None or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    token = create_token(str(admin.id), settings.jwt_secret, settings.jwt_expire_minutes)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=AdminOut)
def get_me(current_admin: Admin = Depends(get_current_admin)):
    return current_admin


@router.put("/me", response_model=AdminOut)
def update_me(
    payload: ProfileUpdateRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, current_admin.password_hash):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Current password is incorrect")

    if payload.new_username is None and payload.new_password is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide new_username and/or new_password",
        )

    if payload.new_username is not None and payload.new_username != current_admin.username:
        taken = (
            db.query(Admin)
            .filter(Admin.username == payload.new_username, Admin.id != current_admin.id)
            .first()
        )
        if taken is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already taken")
        current_admin.username = payload.new_username

    if payload.new_password is not None:
        current_admin.password_hash = hash_password(payload.new_password)

    db.commit()
    db.refresh(current_admin)
    return current_admin
