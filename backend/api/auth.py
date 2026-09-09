from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.db.connection import get_db
from backend.db.models import User

from backend.models.auth import (
    LoginRequest,
    AuthResponse,
    RefreshTokenRequest,
)

from backend.services.auth import (
    verify_password,
    create_access_token,
    create_refresh_token,
)

from backend.stores.refresh_token_store import RefreshTokenStore
from datetime import datetime, timedelta, timezone

refresh_token_store = RefreshTokenStore()

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.post( "/login", response_model=AuthResponse, )

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

    refresh_token = create_refresh_token()

    refresh_expires_at = (
        datetime.now(timezone.utc)
        + timedelta(days=7)
    )

    saved_refresh_token = refresh_token_store.create(
        user_id=str(user.id),
        raw_token=refresh_token,
        expires_at=refresh_expires_at,
    )

    if saved_refresh_token is None:
        raise HTTPException(
            status_code=500,
            detail="Failed to create refresh token",
        )
    
    return AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )

@router.post("/refresh", response_model=AuthResponse)

def refresh_access_token(
    request: RefreshTokenRequest,
):
    stored_token = refresh_token_store.get_by_token(
        request.refresh_token
    )

    if stored_token is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    if stored_token.revoked:
        raise HTTPException(
            status_code=401,
            detail="Refresh token has been revoked",
        )

    now = datetime.now(timezone.utc)

    if stored_token.expires_at <= now:
        raise HTTPException(
            status_code=401,
            detail="Refresh token has expired",
        )

    access_token = create_access_token(
        str(stored_token.user_id)
    )

    return AuthResponse(
        access_token=access_token,
        refresh_token=request.refresh_token,
        token_type="bearer",
    )