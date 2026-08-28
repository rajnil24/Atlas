from fastapi import APIRouter , HTTPException
from pydantic import BaseModel
from backend.stores.message_store import MessageStore
from backend.stores.session_store import SessionStore

class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    message_metadata: dict | None = None

class SendMessageRequest(BaseModel):
    content: str

message_store = MessageStore()
session_store = SessionStore()

router = APIRouter(
    prefix="/messages",
    tags=["Messages"],
) 

@router.post(
    "/{user_id}/sessions/{session_id}/messages",
    response_model=MessageResponse,
)

async def send_message(
    user_id: str,
    session_id: str,
    request: SendMessageRequest,
):
        session = session_store.get_session(
        user_id=user_id,
        session_id=session_id,
        )

        if not session:
            raise HTTPException(
               status_code=404,
               detail="Session not found",
            )

        user_message = message_store.create_message(
        session_id=session_id,
        role="user",
        content=request.content,
        )

        final_answer = "done"
        
        assistant_message = message_store.create_message(
                            session_id=session_id,
                            role="assistant",
                            content=final_answer,
                            )

        return MessageResponse(
            id=assistant_message.id,
            session_id=assistant_message.session_id,
            role=assistant_message.role,
            content=assistant_message.content,
            message_metadata=assistant_message.message_metadata,
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