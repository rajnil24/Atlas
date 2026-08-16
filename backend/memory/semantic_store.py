import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.exc import SQLAlchemyError
from backend.db.connection import SessionLocal
from backend.db.models import Fact

DUPLICATE_THRESHOLD = 0.90
UPDATE_THRESHOLD = 0.75


class SemanticStore:
    """Owns all reads/writes to the semantic (durable facts) table,
    including similarity-based reconciliation before writing."""

    def find_similar(self, user_id: str, embedding: list[float], limit: int = 3) -> list[tuple[Fact, float]]:
        db = SessionLocal()
        try:
            results = (
                db.query(Fact, Fact.embedding.cosine_distance(embedding).label("distance"))
                .filter(Fact.user_id == user_id)
                .order_by("distance")
                .limit(limit)
                .all()
            )
            # cosine_distance = 1 - cosine_similarity, so convert back
            return [(fact, 1 - distance) for fact, distance in results]
        finally:
            db.close()

    def upsert_fact(
        self,
        user_id: str,
        fact_text: str,
        embedding: list[float],
        category: str,
        confidence: float,
        source_episode_id: Optional[str] = None,
    ) -> str:
        similar = self.find_similar(user_id, embedding, limit=1)

        db = SessionLocal()
        try:
            if similar and similar[0][1] >= DUPLICATE_THRESHOLD:
                existing_fact, _ = similar[0]
                existing_fact.updated_at = datetime.now(timezone.utc)
                db.merge(existing_fact)
                db.commit()
                return existing_fact.id

            if similar and similar[0][1] >= UPDATE_THRESHOLD:
                existing_fact, _ = similar[0]
                existing_fact.fact_text = fact_text
                existing_fact.embedding = embedding
                existing_fact.confidence = confidence
                existing_fact.updated_at = datetime.now(timezone.utc)
                db.merge(existing_fact)
                db.commit()
                return existing_fact.id

            new_fact = Fact(
                id=str(uuid.uuid4()),
                user_id=user_id,
                fact_text=fact_text,
                embedding=embedding,
                category=category,
                confidence=confidence,
                source_episode_id=source_episode_id,
            )
            db.add(new_fact)
            db.commit()
            return new_fact.id

        except SQLAlchemyError as e:
            db.rollback()
            print(f"[SemanticStore] upsert failed: {e}")
            return None
        finally:
            db.close()

    def retrieve(self, user_id: str, query_embedding: list[float], top_k: int = 5) -> list[Fact]:
        matches = self.find_similar(user_id, query_embedding, limit=top_k)
        return [fact for fact, score in matches]