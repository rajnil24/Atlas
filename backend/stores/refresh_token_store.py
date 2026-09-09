import uuid
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from backend.db.connection import SessionLocal
from backend.db.models import RefreshToken
from backend.services.auth import hash_refresh_token


class RefreshTokenStore:

    def create(
        self,
        user_id: str,
        raw_token: str,
        expires_at: datetime,
    ):
        db = SessionLocal()

        try:
            token = RefreshToken(
                id=str(uuid.uuid4()),
                user_id=str(user_id),
                token_hash=hash_refresh_token(raw_token),
                expires_at=expires_at,
                revoked=False,
            )

            db.add(token)
            db.commit()
            db.refresh(token)

            return token

        except SQLAlchemyError:
            db.rollback()
            return None

        finally:
            db.close()

    def get_by_token(self, raw_token: str):
        token_hash = hash_refresh_token(raw_token)

        db = SessionLocal()

        try:
            return (
                db.query(RefreshToken)
                .filter(
                    RefreshToken.token_hash == token_hash
                )
                .first()
            )

        finally:
            db.close()

    def revoke(self, token_id: str) -> bool:
        db = SessionLocal()

        try:
            token = (
                db.query(RefreshToken)
                .filter(RefreshToken.id == token_id)
                .first()
            )

            if not token:
                return False

            token.revoked = True
            db.commit()

            return True

        except SQLAlchemyError:
            db.rollback()
            return False

        finally:
            db.close()