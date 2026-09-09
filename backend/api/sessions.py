from fastapi import APIRouter, HTTPException , Depends
from pydantic import BaseModel
from backend.stores.session_store import SessionStore
from backend.dependencies.auth import get_current_user


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"],
)

session_store = SessionStore()


class CreateSessionRequest(BaseModel):
    pass

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

def create_session(current_user=Depends(get_current_user),):

    session = session_store.create_session(
    user_id=current_user.id,
    )

    if not session:
        raise HTTPException(
            status_code=500,
            detail="Failed to create session",
        )

    return SessionResponse(
        id=str(session.id),
        user_id=str(session.user_id),
        title=session.title,
    )

@router.get(
    "",
    response_model=list[SessionResponse],
)

def get_user_sessions(current_user=Depends(get_current_user),):

    user_id = str(current_user.id)

    sessions = session_store.get_user_sessions(user_id)

    return [
        SessionResponse(
            id=str(session.id),
            user_id=str(session.user_id),
            title=session.title,
        )
        for session in sessions
    ]

@router.patch(
    "/{session_id}",
    response_model=SessionResponse,
)
def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    current_user=Depends(get_current_user),
):
    user_id = str(current_user.id)

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
        id=str(session.id),
        user_id=str(session.user_id),
        title=session.title,
    )

@router.delete(
    "/{session_id}",
)
def delete_session(
    session_id: str,
    current_user=Depends(get_current_user),
): 
    
    user_id = str(current_user.id)
    
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