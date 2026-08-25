from sqlalchemy.exc import SQLAlchemyError
from backend.db.connection import SessionLocal
from backend.db.models import Message
from backend.db.models import ChatSession

class MessageStore:

    def create_message(
        self,
        session_id: str,
        role: str,
        content: str,
        message_metadata: dict | None = None,
    ) -> Message | None:

        db = SessionLocal()

        try:
            message = Message(
                session_id=session_id,
                role=role,
                content=content,
                message_metadata=message_metadata,
            )

            db.add(message)
            db.commit()
            db.refresh(message)

            return message

        except SQLAlchemyError as e:
            db.rollback()
            print(f"[MessageStore] create failed: {e}")
            return None

        finally:
            db.close()

    def get_message(
        self,
        message_id: str,
    ) -> Message | None:

        db = SessionLocal()

        try:
            return (
                db.query(Message)
                .filter(Message.id == message_id)
                .first()
            )

        finally:
            db.close()

    def get_user_session_messages(
        self,
        user_id : str ,
        session_id: str,
        limit: int = 50,
    ) -> list[Message]:

        db = SessionLocal()

        try:
            return (
               db.query(Message)
               .join(ChatSession, Message.session_id == ChatSession.id)
               .filter(
                  Message.session_id == session_id,
                  ChatSession.user_id == user_id,
                )
               .order_by(Message.created_at.asc())
               .limit(limit)
               .all()
            )
        finally:
            db.close()