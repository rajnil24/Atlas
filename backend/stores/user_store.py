from sqlalchemy.exc import SQLAlchemyError
from backend.db.connection import SessionLocal
from backend.db.models import User


class UserStore:

    def create_user(
        self,
        email: str,
        name: str | None = None,
    ) -> User | None:

        db = SessionLocal()

        try:
            user = User(
                email=email,
                name=name,
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            return user

        except SQLAlchemyError as e:
            db.rollback()
            print(f"[UserStore] create failed: {e}")
            return None

        finally:
            db.close()

    def get_user(self, user_id: str) -> User | None:

        db = SessionLocal()

        try:
            return (
                db.query(User)
                .filter(User.id == user_id)
                .first()
            )

        finally:
            db.close()

    def get_user_by_email(self, email: str) -> User | None:

        db = SessionLocal()

        try:
            return (
                db.query(User)
                .filter(User.email == email)
                .first()
            )

        finally:
            db.close()