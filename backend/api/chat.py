from fastapi import APIRouter, Depends
from backend.dependencies.auth import get_current_user
from backend.models.chat import ChatRequest

router = APIRouter(
tags=["Chat"]
)

@router.post("/chat")

def chat(
request: ChatRequest,
current_user=Depends(get_current_user),
):
    print(current_user.id)

    return {
       "message": request.message,
       "user_id": str(current_user.id),
    }