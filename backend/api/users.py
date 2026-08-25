from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from backend.stores.user_store import UserStore


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)

user_store = UserStore()


class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str | None = None


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

    user = user_store.create_user(
        email=request.email,
        name=request.name,
    )

    if not user:
        raise HTTPException(
            status_code=500,
            detail="Failed to create user",
        )

    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
    )