import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from backend.db.connection import SessionLocal
from backend.db.models import Episode


class EpisodicStore:
    """Owns all reads/writes to the episodic (raw turn history) table."""

    def write_episode(
        self,
        user_id: str,
        session_id: str,
        role: str,
        content: str,
        meta : dict | None = None ,
    ) -> Optional[str]:
        db = SessionLocal()
        try:
            episode = Episode(
                id=str(uuid.uuid4()),
                user_id=user_id,
                session_id=session_id,
                meta=meta,
                role=role,
                content=content,
                created_at=datetime.now(timezone.utc),
            )
            db.add(episode)
            db.commit()
            print ("episode created , ->" , episode)
            return episode.episode_id
        except SQLAlchemyError as e:
            db.rollback()
            print(f"[EpisodicStore] write failed: {e}")
            return None
        finally:
            db.close()

    def write_episodes_batch(self, episodes: list[dict]) -> int:
        db = SessionLocal()
        try:
            objects = [
                Episode(
                    id=str(uuid.uuid4()),
                    user_id=e["user_id"],
                    session_id=e["session_id"],
                    meta=e.get("meta"),
                    role=e["role"],
                    content=e["content"],
                    created_at=datetime.now(timezone.utc),
                )
                for e in episodes
            ]
            db.bulk_save_objects(objects)
            db.commit()
            print("bulk objects dispatched")
            return len(objects)
        except SQLAlchemyError as e:
            db.rollback()
            print(f"[EpisodicStore] batch write failed: {e}")
            return 0
        finally:
            db.close()

    def get_session_history(
        self,
        session_id: str,
        limit: int = 50,
        before: Optional[datetime] = None,
    ) -> list[Episode]:
        db = SessionLocal()
        try:
            query = db.query(Episode).filter(Episode.session_id == session_id)
            if before:
                query = query.filter(Episode.created_at < before)
            return query.order_by(Episode.created_at.desc()).limit(limit).all()
        finally:
            db.close()