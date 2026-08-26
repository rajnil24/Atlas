from fastapi import APIRouter
from pydantic import BaseModel
from backend.stores.message_store import MessageStore

class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    message_metadata: dict | None = None

message_store = MessageStore()

router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
) 

@router.get(
    "/{user_id}/sessions/{session_id}/messages",
    response_model=list[MessageResponse],
)

def get_session_messages(
    user_id: str,
    session_id: str,
    limit: int = 50,
):
    messages = message_store.get_user_session_messages(
        user_id=user_id,
        session_id=session_id,
        limit=limit,
    )

    return [
        MessageResponse(
            id=message.id,
            session_id=message.session_id,
            role=message.role,
            content=message.content,
            message_metadata=message.message_metadata,
        )
        for message in messages
    ]