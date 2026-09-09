from fastapi import APIRouter , Depends
from pydantic import BaseModel
from backend.stores.message_store import MessageStore
from backend.dependencies.auth import get_current_user


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
    "/{session_id}",
    response_model=list[MessageResponse],
)
def get_session_messages(
    session_id: str,
    limit: int = 50,
    current_user=Depends(get_current_user),
):
    user_id = str(current_user.id)
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