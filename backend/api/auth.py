from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.db.connection import get_db
from backend.db.models import User

from backend.models.auth import (
    SignupRequest,
    LoginRequest,
    AuthResponse,
)

from backend.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(
    request: SignupRequest,
    db: Session = Depends(get_db),
):

    existing_user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    password_hash = hash_password(request.password)

    user = User(
        email=request.email,
        name=request.name,
        password_hash=password_hash,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(user.id)

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
    )


@router.post(
    "/login",
    response_model=AuthResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):

    user = (
        db.query(User)
        .filter(User.email == request.email)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if user.password_hash is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account requires password setup",
        )

    password_valid = verify_password(
        request.password,
        user.password_hash,
    )

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user.id)

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
    )