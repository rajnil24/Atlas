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

class UpdateSessionRequest(BaseModel):
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

@router.patch(
    "/{user_id}/sessions/{session_id}",
    response_model=SessionResponse,
)
def update_session(
    user_id: str,
    session_id: str,
    request: UpdateSessionRequest,
):

    session = session_store.update_session_title(
        user_id=user_id,
        session_id=session_id,
        title=request.title,
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    return SessionResponse(
        id=session.id,
        user_id=session.user_id,
        title=session.title,
    )

@router.delete(
    "/{user_id}/sessions/{session_id}",
)
def delete_session(
    user_id: str,
    session_id: str,
):

    deleted = session_store.delete_session(
        user_id=user_id,
        session_id=session_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    return {
        "message": "Session deleted successfully",
        "session_id": session_id,
    }