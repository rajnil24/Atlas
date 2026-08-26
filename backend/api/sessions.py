from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.stores.session_store import SessionStore
from backend.stores.user_store import UserStore


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)

session_store = SessionStore()
user_store = UserStore()


class CreateSessionRequest(BaseModel):
    user_id: str

class SessionResponse(BaseModel):
    id: str
    user_id: str
    title: str

@router.post(
    "",
    response_model=SessionResponse,
)

def create_session(request: CreateSessionRequest):

    user = user_store.get_user_by_id(
        request.user_id
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    session = session_store.create_session(
        user_id=user.id,
    )

    return SessionResponse(
        id=session.id,
        user_id=session.user_id,
        title=session.title,
    )

@router.get(
    "/{user_id}",
    response_model=list[SessionResponse],
)

def get_user_sessions(user_id: str):

    user = user_store.get_user_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    sessions = session_store.get_user_sessions(user_id)

    return [
        SessionResponse(
            id=session.id,
            user_id=session.user_id,
            title=session.title,
        )
        for session in sessions
    ]