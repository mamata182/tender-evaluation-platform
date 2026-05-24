from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta

from app.database import get_db
from app.models.db_models import User
from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
    oauth2_scheme,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class UserSignup(BaseModel):
    full_name: str
    email: str
    password: str
    confirm_password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


@router.post("/signup", response_model=TokenOut)
def signup(data: UserSignup, db: Session = Depends(get_db)):
    print(f"[SIGNUP] Email: {data.email}")

    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if len(data.password) < 6:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 6 characters"
        )

    email = data.email.lower().strip()

    existing = db.query(User).filter(User.email == email).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered. Please login instead."
        )

    user = User(
        full_name=data.full_name.strip(),
        email=email,
        hashed_password=get_password_hash(data.password),
        is_active=True,
        role="user"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    print(f"[SIGNUP] User created: {user.email}")

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }


@router.post("/login", response_model=TokenOut)
def login(data: UserLogin, db: Session = Depends(get_db)):
    print(f"[LOGIN] Email: {data.email}")

    email = data.email.lower().strip()

    user = db.query(User).filter(User.email == email).first()

    if not user:
        print("[LOGIN] User not found")
        raise HTTPException(status_code=401, detail="Invalid email or password")

    password_ok = verify_password(data.password, user.hashed_password)

    print(f"[LOGIN] Password valid: {password_ok}")

    if not password_ok:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Account is inactive")

    token = create_access_token(
        data={"sub": user.email},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    print(f"[LOGIN] Success: {user.email}")

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }


@router.get("/me", response_model=UserOut)
def get_me(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    email = decode_token(token)

    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}