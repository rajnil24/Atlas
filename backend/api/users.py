from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr , Field
from backend.services.auth import hash_password
from backend.stores.user_store import UserStore


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

user_store = UserStore()


class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str | None = Field(default=None, max_length=100)
    password: str = Field(
        min_length=8,
        max_length=72,
    )


class UserResponse(BaseModel):
    id: str
    email: str
    name: str | None


@router.post(
    "",
    response_model=UserResponse,
)

def create_user(request: CreateUserRequest):

    existing_user = user_store.get_user_by_email(
        request.email
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="User with this email already exists",
        )

    try:
        password_hash = hash_password(
            request.password
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    user = user_store.create_user(
        email=request.email,
        name=request.name,
        password_hash=password_hash,
    )

    if not user:
        raise HTTPException(
            status_code=500,
            detail="Failed to create user",
        )

    return UserResponse(
        id=str(user.id),
        email=user.email,
        name=user.name,
    )