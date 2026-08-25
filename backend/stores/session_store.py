from sqlalchemy.exc import SQLAlchemyError
from backend.db.connection import SessionLocal
from backend.db.models import ChatSession


class SessionStore:

    def create_session(
        self,
        user_id: str,
        title: str = "New Chat",
    ) -> ChatSession | None:

        db = SessionLocal()

        try:
            session = ChatSession(
                user_id=user_id,
                title=title,
            )

            db.add(session)
            db.commit()
            db.refresh(session)

            return session

        except SQLAlchemyError as e:
            db.rollback()
            print(f"[SessionStore] create failed: {e}")
            return None

        finally:
            db.close()

    def get_session(
        self,
        user_id : str ,
        session_id: str,
    ) -> ChatSession | None:

        db = SessionLocal()

        try:
            return (
                db.query(ChatSession)
                .filter(
                    ChatSession.id == session_id , 
                    ChatSession.user_id == user_id ,
                    )
                .first()
            )

        finally:
            db.close()

    def get_user_sessions(
        self,
        user_id: str,
    ) -> list[ChatSession]:

        db = SessionLocal()

        try:
            return (
                db.query(ChatSession)
                .filter(ChatSession.user_id == user_id)
                .order_by(ChatSession.updated_at.desc())
                .all()
            )

        finally:
            db.close()